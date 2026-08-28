import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User, Organization, UserSession, AuditEvent
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_user

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    display_name: str
    role: str
    organization_id: str
    organization_name: str

class UserProfileResponse(BaseModel):
    id: str
    email: str
    display_name: str
    role: str
    status: str
    organization_id: str
    organization_name: str
    mfa_enabled: bool
    last_login_at: Optional[datetime] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/login", response_model=LoginResponse)
def login(
    req: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authenticates user credentials with account lockout protection (5 failed attempts -> 15 min lock),
    attaches HttpOnly, SameSite=Lax cookie, generates signed JWT, and logs audit event.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    user = db.query(User).filter(User.email == req.email).first()

    # Anti-enumeration response
    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        org = db.query(Organization).first()
        audit = AuditEvent(
            organization_id=org.id if org else "unknown",
            actor_email=req.email,
            action="LOGIN_FAILURE",
            target_type="User",
            target_id=req.email,
            outcome="FAILURE",
            event_metadata={"reason": "User not found"}
        )
        db.add(audit)
        db.commit()
        raise invalid_credentials_exception

    # Check account lock status (naive datetime comparison for SQLite)
    locked_until_naive = user.locked_until.replace(tzinfo=None) if user.locked_until else None
    if locked_until_naive and locked_until_naive > now:
        audit = AuditEvent(
            organization_id=user.organization_id,
            actor_email=user.email,
            action="LOGIN_FAILURE",
            target_type="User",
            target_id=user.id,
            outcome="FAILURE",
            event_metadata={"reason": "Account locked due to excessive failed login attempts"}
        )
        db.add(audit)
        db.commit()
        raise invalid_credentials_exception

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status.lower()}. Please contact administrator.",
        )

    if not verify_password(req.password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= 5:
            user.locked_until = now + timedelta(minutes=15)
            audit_lock = AuditEvent(
                organization_id=user.organization_id,
                actor_email=user.email,
                action="ACCOUNT_LOCKED",
                target_type="User",
                target_id=user.id,
                outcome="SUCCESS",
                event_metadata={"reason": "5 consecutive failed login attempts"}
            )
            db.add(audit_lock)

        audit = AuditEvent(
            organization_id=user.organization_id,
            actor_email=user.email,
            action="LOGIN_FAILURE",
            target_type="User",
            target_id=user.id,
            outcome="FAILURE",
            event_metadata={"reason": "Incorrect password", "failed_attempts": user.failed_login_count}
        )
        db.add(audit)
        db.commit()
        raise invalid_credentials_exception

    # Successful login: reset lock & failed counter
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = now

    # Create UserSession record
    session_token = str(uuid.uuid4())
    user_session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=now + timedelta(hours=8)
    )
    db.add(user_session)
    db.flush()

    audit = AuditEvent(
        organization_id=user.organization_id,
        actor_email=user.email,
        action="LOGIN_SUCCESS",
        target_type="User",
        target_id=user.id,
        outcome="SUCCESS",
        event_metadata={"role": user.role}
    )
    db.add(audit)
    db.commit()

    # Create JWT access token
    jwt_claims = {
        "sub": user.id,
        "email": user.email,
        "org_id": user.organization_id,
        "role": user.role,
        "session_id": user_session.id
    }
    access_token = create_access_token(jwt_claims)

    # Attach HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        path="/api/v1"
    )

    org_name = user.organization.name if user.organization else "Anurag Technologies"

    return LoginResponse(
        access_token=access_token,
        user_id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        organization_id=user.organization_id,
        organization_name=org_name
    )

@router.post("/logout")
def logout(
    response: Response,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logs out authenticated user, revokes active DB session, and clears HttpOnly cookie.
    """
    # Revoke active UserSessions for user
    active_sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.revoked_at.is_(None)
    ).all()

    now = datetime.now(timezone.utc)
    for s in active_sessions:
        s.revoked_at = now

    audit = AuditEvent(
        organization_id=current_user.organization_id,
        actor_email=current_user.email,
        action="LOGOUT",
        target_type="User",
        target_id=current_user.id,
        outcome="SUCCESS"
    )
    db.add(audit)
    db.commit()

    # Delete HttpOnly cookie
    response.delete_cookie(key="access_token", path="/api/v1")

    return {"status": "SUCCESS", "message": "Successfully logged out and session revoked"}

@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Returns current authenticated user profile and role details.
    """
    org_name = current_user.organization.name if current_user.organization else "Anurag Technologies"
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        role=current_user.role,
        status=current_user.status,
        organization_id=current_user.organization_id,
        organization_name=org_name,
        mfa_enabled=current_user.mfa_enabled,
        last_login_at=current_user.last_login_at
    )

@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Changes user password securely and revokes all active sessions to force re-login.
    """
    if not verify_password(req.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password verification failed"
        )

    current_user.password_hash = get_password_hash(req.new_password)
    current_user.password_changed_at = datetime.now(timezone.utc)

    # Revoke sessions on password change
    now = datetime.now(timezone.utc)
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.revoked_at.is_(None)
    ).all()
    for s in sessions:
        s.revoked_at = now

    audit = AuditEvent(
        organization_id=current_user.organization_id,
        actor_email=current_user.email,
        action="PASSWORD_CHANGED",
        target_type="User",
        target_id=current_user.id,
        outcome="SUCCESS"
    )
    db.add(audit)
    db.commit()

    return {"status": "SUCCESS", "message": "Password changed successfully. Active sessions revoked."}
