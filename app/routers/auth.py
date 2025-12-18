from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserResponse, TokenResponse, LoginRequest
from app.crud import create_user, get_users, get_user_by_email
from app.database import get_db
from app.security import verify_password, create_access_token, create_refresh_token
from fastapi import HTTPException, status
from app.dependencies import get_current_user
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import get_user_by_email
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


router = APIRouter(prefix='/api/auth')

@router.post('/register', response_model=UserResponse)
async def UserRegisteration(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user)

@router.get('/users', response_model=list[UserResponse])
async def AllUsers(db: AsyncSession = Depends(get_db)):
    return await get_users(db)

@router.post("/login", response_model=TokenResponse)
async def UserLogin(user: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, user.email)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token({"sub": db_user.email})
    refresh_token = create_refresh_token({"sub": db_user.email})

    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=24*60*60 #1 day
    )

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=7*24*60*60 #7 days

    )

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.get("/user/me", response_model = UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    return current_user


@router.post("/refresh")
async def refresh_token_reload(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token found")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Create new access token
    new_access_token = create_access_token({"sub": email})

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,   # True in production
        samesite="lax",
        max_age=24*60*60
    )

    return {"message": "Access token refreshed"}



