from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from dotenv import load_dotenv
from uuid import UUID
import os

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import (
    UserCreate,
    LoginRequest,
    UserResponse,
    UserUpdateSchema
)
from app.crud import (
    create_user,
    get_users,
    get_user_by_email,
    update_user,
    delete_user
)
from app.security import (
    verify_password,
    create_access_token,
    create_refresh_token
)

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

router = APIRouter(prefix='/api/auth', tags=['Auth'])

# ---------------- REGISTER ----------------
@router.post('/user-register', response_model=UserResponse, status_code=201)
async def UserRegister(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user)

# ---------------- ALL USERS ----------------
@router.get('/users', response_model=list[UserResponse], status_code=200)
async def GetUsers(db: AsyncSession = Depends(get_db)):
    return await get_users(db)

    