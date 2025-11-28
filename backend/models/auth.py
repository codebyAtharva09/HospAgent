from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field

class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    RECEPTION = "RECEPTION"
    PHARMACIST = "PHARMACIST"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str
    hashed_password: str
    role: UserRole
    is_active: bool = True
