from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

from app.schemas import UserCreate, LoginRequest
from app.crud import create_user, get_users, get_user_by_email
from app.database import get_db
from app.security import verify_password, create_access_token, create_refresh_token
from app.dependencies import get_current_user


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


class AuthController:

    async def register(self, user: UserCreate, db: AsyncSession = Depends(get_db)):
        return await create_user(db, user)
    
    async def all_users(self, db: AsyncSession = Depends(get_db)):
        return await get_users(db)
    
    async def login(self, user: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
        db_user = await get_user_by_email(db, user.email)

        if not db_user or not verify_password(user.password, db_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        access_token = create_access_token({"sub": db_user.email})
        refresh_token = create_refresh_token({"sub": db_user.email})

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=24 * 60 * 60
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=7 * 24 * 60 * 60
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    async def me(self, current_user=Depends(get_current_user)):
        return current_user

    async def refresh(self, request: Request, response: Response):
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

        new_access_token = create_access_token({"sub": email})

        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            max_age=24 * 60 * 60
        )

        return {"message": "Access token refreshed"}

    




