from typing import Optional, List, Callable
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.core.security import decode_access_token
from app.models import User, Organization, UserSession, AuditEvent, OrganizationMembership

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Server-side authentication dependency.
    Extracts JWT session token from:
    1. HttpOnly cookie ('access_token')
    2. Authorization Bearer header

    Validates signature, issuer, subject, active user status, and checks DB UserSession
    revocation status to prevent session replay post-logout or revocation.
    """
    raw_token = request.cookies.get("access_token")
    if not raw_token:
        raw_token = token
    if not raw_token and authorization and authorization.startswith("Bearer "):
        raw_token = authorization.split(" ")[1]

    if raw_token:
        payload = decode_access_token(raw_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Issuer validation
        if payload.get("iss") != settings.PROJECT_NAME:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        session_id = payload.get("session_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Database session revocation check
        if session_id:
            user_session = db.query(UserSession).filter(UserSession.id == session_id).first()
            if user_session and user_session.revoked_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session has been revoked",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account not found",
            )

        if user.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User account is {user.status.lower()}",
            )

        return user

    # Demo mode fallback if unauthenticated
    if settings.DEMO_MODE:
        user = db.query(User).filter(User.email == "admin@anurag.tech").first()
        if user:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_org_id(
    x_organization_id: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> str:
    """
    Derives Organization ID for database queries.
    If X-Organization-ID header is supplied, verifies user has active membership
    or SUPER_ADMIN role in that target organization.
    Otherwise, defaults to user's primary organization_id.
    """
    if x_organization_id and x_organization_id != current_user.organization_id:
        if current_user.role == "SUPER_ADMIN":
            return x_organization_id

        # Check active membership in requested organization
        mem = db.query(OrganizationMembership).filter(
            OrganizationMembership.user_id == current_user.id,
            OrganizationMembership.organization_id == x_organization_id,
            OrganizationMembership.status == "ACTIVE"
        ).first()
        if mem:
            return x_organization_id

        # In DEMO_MODE fallback for unauthenticated test helper setup
        if settings.DEMO_MODE and current_user.email == "admin@anurag.tech":
            return x_organization_id

    return current_user.organization_id

def require_role(allowed_roles: List[str]) -> Callable:
    """
    Dependency factory enforcing Role-Based Access Control (RBAC).
    Denies request with 403 Forbidden and logs authorization_denied audit event.
    Re-verifies current database role to ensure post-issuance role changes take effect immediately.
    """
    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if current_user.role not in allowed_roles and "ALL" not in allowed_roles:
            # Audit log authorization failure
            audit = AuditEvent(
                organization_id=current_user.organization_id,
                actor_email=current_user.email,
                action="AUTHORIZATION_DENIED",
                target_type="RolePermission",
                target_id=current_user.role,
                outcome="DENIED",
                event_metadata={
                    "user_role": current_user.role,
                    "required_roles": allowed_roles,
                    "reason": "Insufficient privileges"
                }
            )
            db.add(audit)
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' lacks permission for this action. Required: {allowed_roles}"
            )
        return current_user

    return role_checker
