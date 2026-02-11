from pydantic import BaseModel, EmailStr, field_validator, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr
    password: str = Field(..., max_length=10, min_length=6)

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    #refresh_token: str
    token_type: str = 'bearer'

class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=50)

    class Config:
        from_attributes = True