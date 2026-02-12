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
    deactivate_user,
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
    
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is deactivated. Please activate your account."
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

# ---------------- CURRENT USER ----------------
@router.get('/user-profile', response_model=UserResponse)
async def AuthUser(current_user = Depends(get_current_user)):
    return current_user

# ---------------- REFRESH TOKEN ----------------
@router.post("/token/refresh", response_model=LoginResponse)
async def AccessTokenRefresh(request: Request, response: Response):
    token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(status_code=401, detail="No refresh token found")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        id = payload.get("sub")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": str(id)})

    return {
        'access_token': new_access_token,
        'token_type': 'bearer'
    }

@router.patch('/user-update', response_model=UserResponse)
async def UserUpdate(
    user_update: UserUpdateSchema,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    update_data = user_update.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update"
        )
    
    return await update_user(db, current_user.id, update_data)
    
@router.patch('/user-deactivate', status_code=status.HTTP_204_NO_CONTENT)
async def DeactivateUser(user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await deactivate_user(db, user.id)
    return {"message": "Account deactivated successfully"}

