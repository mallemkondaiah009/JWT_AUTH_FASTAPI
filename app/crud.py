from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User
from app.schemas import UserCreate
from app.security import hash_password



async def create_user(db:AsyncSession, user:UserCreate):
    hashed_pwd = hash_password(user.password)

    user = User(
        username=user.username,
        email=user.email,
        password=hashed_pwd
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()