from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from db_config import get_session
from models.auth import User, UserRole
from services.auth_service import (
    authenticate_user, 
    create_access_token, 
    get_current_user, 
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta
from pydantic import BaseModel

router = APIRouter(tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "role": user.role,
            "email": user.email
        }
    }

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
