from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hash_password: str):
    return pwd_context.verify(plain_password,hash_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update(
        {'exp': expire}
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

