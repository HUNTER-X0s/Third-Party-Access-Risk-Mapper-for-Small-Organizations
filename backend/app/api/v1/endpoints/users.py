from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User, OrganizationMembership, AuditEvent
from app.core.security import get_password_hash
from app.api.deps import get_current_user, require_role, get_current_org_id

router = APIRouter()

class UserOut(BaseModel):
    id: str
    organization_id: str
    email: str
    display_name: str
    role: str
    status: str
    mfa_enabled: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CreateUserRequest(BaseModel):
    email: str
    display_name: str
    role: str = "VIEWER"
    password: Optional[str] = "DemoPass123!"

class UpdateRoleRequest(BaseModel):
    role: str

class UpdateStatusRequest(BaseModel):
    status: str  # ACTIVE, SUSPENDED, DISABLED

ALLOWED_ADMIN_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN"]

@router.get("", response_model=List[UserOut])
def list_users(
    current_user: User = Depends(require_role(ALLOWED_ADMIN_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Lists users belonging strictly to the authenticated user's organization.
    Restricted to SUPER_ADMIN and SECURITY_ADMIN.
    """
    users = db.query(User).filter(User.organization_id == org_id).all()
    return [UserOut.model_validate(u) for u in users]

@router.post("", response_model=UserOut)
def create_user(
    req: CreateUserRequest,
    current_user: User = Depends(require_role(ALLOWED_ADMIN_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Creates/invites a user account within the authenticated user's organization.
    """
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists"
        )

    valid_roles = ["SUPER_ADMIN", "SECURITY_ADMIN", "IT_ADMIN", "AUDITOR", "APP_OWNER", "DATA_OWNER", "VIEWER"]
    if req.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{req.role}'. Valid roles: {valid_roles}"
        )

    new_user = User(
        organization_id=org_id,
        email=req.email,
        display_name=req.display_name,
        password_hash=get_password_hash(req.password or "DemoPass123!"),
        role=req.role,
        status="ACTIVE"
    )
    db.add(new_user)
    db.flush()

    membership = OrganizationMembership(
        user_id=new_user.id,
        organization_id=org_id,
        role=req.role,
        status="ACTIVE"
    )
    db.add(membership)

    audit = AuditEvent(
        organization_id=org_id,
        actor_email=current_user.email,
        action="USER_CREATED",
        target_type="User",
        target_id=new_user.id,
        outcome="SUCCESS",
        event_metadata={"created_email": new_user.email, "role": new_user.role}
    )
    db.add(audit)
    db.commit()

    return UserOut.model_validate(new_user)

@router.patch("/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: str,
    req: UpdateRoleRequest,
    current_user: User = Depends(require_role(ALLOWED_ADMIN_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Updates a user's role with server-side organization scope check.
    Prevents self-demotion if current user is the target.
    """
    user = db.query(User).filter(User.id == user_id, User.organization_id == org_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in organization")

    valid_roles = ["SUPER_ADMIN", "SECURITY_ADMIN", "IT_ADMIN", "AUDITOR", "APP_OWNER", "DATA_OWNER", "VIEWER"]
    if req.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role '{req.role}'")

    # Prevent self-lockout
    if user.id == current_user.id and req.role != current_user.role:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    old_role = user.role
    user.role = req.role

    # Update membership as well
    mem = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.organization_id == org_id
    ).first()
    if mem:
        mem.role = req.role

    audit = AuditEvent(
        organization_id=org_id,
        actor_email=current_user.email,
        action="ROLE_CHANGED",
        target_type="User",
        target_id=user.id,
        outcome="SUCCESS",
        event_metadata={"target_email": user.email, "old_role": old_role, "new_role": req.role}
    )
    db.add(audit)
    db.commit()

    return UserOut.model_validate(user)

@router.patch("/{user_id}/status", response_model=UserOut)
def update_user_status(
    user_id: str,
    req: UpdateStatusRequest,
    current_user: User = Depends(require_role(ALLOWED_ADMIN_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Suspends or reactivates a user account.
    """
    user = db.query(User).filter(User.id == user_id, User.organization_id == org_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in organization")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change status of your own account")

    old_status = user.status
    user.status = req.status

    audit = AuditEvent(
        organization_id=org_id,
        actor_email=current_user.email,
        action="USER_STATUS_CHANGED",
        target_type="User",
        target_id=user.id,
        outcome="SUCCESS",
        event_metadata={"target_email": user.email, "old_status": old_status, "new_status": req.status}
    )
    db.add(audit)
    db.commit()

    return UserOut.model_validate(user)
