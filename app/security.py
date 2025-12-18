from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS'))


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

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update(
        {'exp': expire, 'type': 'refresh'}
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


