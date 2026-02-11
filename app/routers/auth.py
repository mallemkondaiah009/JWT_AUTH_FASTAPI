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
    LoginResponse,
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

# ---------------- LOGIN ----------------
@router.post('/user-login', response_model=LoginResponse)
async def UserLogin(user: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password'
        )
    
    access_token = create_access_token({'sub': str(db_user.id)})
    refresh_token = create_refresh_token({'sub': str(db_user.id)})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        path='/',
        samesite='lax',
        max_age=7 * 24 * 60 * 60
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }