
from jose import jwt, JWTError, ExpiredSignatureError
import os
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import get_user_by_id
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()
security = HTTPBearer()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    except ExpiredSignatureError:
        raise HTTPException(401, "Token expired")

    except JWTError:
        raise HTTPException(401, "Invalid token")

    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(404, "User not found")

    return user