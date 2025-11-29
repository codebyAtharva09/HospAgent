from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import json
import os

from db_config import get_session
from models.auth import User, UserRole
from services.auth_service import get_current_user, require_roles, get_password_hash

router = APIRouter(prefix="/api/admin", tags=["admin"])

# --- User Management Models ---

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole

class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool

from services.notify import (
    NotificationConfig, 
    load_notification_config, 
    save_notification_config
)

# --- User Management Endpoints ---

@router.get("/users", response_model=List[UserResponse])
def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    users = session.exec(select(User)).all()
    return users

@router.post("/users", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    # Check if user exists
    existing_user = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_pwd,
        role=user_in.role,
        is_active=True
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.role:
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
        
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    session.delete(user)
    session.commit()
    return {"ok": True}

# --- Notification Config Endpoints ---

@router.get("/notification-config", response_model=NotificationConfig)
def get_notification_config(
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    return load_notification_config()

@router.put("/notification-config", response_model=NotificationConfig)
def update_notification_config(
    config: NotificationConfig,
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    save_notification_config(config)
    return config
