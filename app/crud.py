from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from uuid import UUID

from app.models import User
from app.schemas import UserCreate
from app.security import hash_password



async def create_user(db: AsyncSession, user: UserCreate):
    # Check if email already exists
    email_query = select(User).where(User.email == user.email)
    email_result = await db.execute(email_query)
    existing_email = email_result.scalar_one_or_none()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Check if username already exists
    username_query = select(User).where(User.username == user.username)
    username_result = await db.execute(username_query)
    existing_username = username_result.scalar_one_or_none()
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Hash password
    hashed_pwd = hash_password(user.password)

    # Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_pwd
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User creation failed due to database constraint"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user"
        )

async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def update_user(db: AsyncSession, user_id: UUID, update_data: dict):
    # Fetch user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Apply updates only if data provided
    if not update_data:
        return user  # Nothing to do

    protected_fields = {"id", "password", "created_at", "updated_at"}

    for field, value in update_data.items():
        if hasattr(user, field) and field not in protected_fields:
            setattr(user, field, value)

    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update: username or email already taken"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
    
# async def delete_user(db: AsyncSession, user_id: UUID):
#     # Fetch user
#     result = await db.execute(select(User).where(User.id == user_id))
#     user = result.scalar_one_or_none()

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

#     try:
#         await db.delete()
#         await db.refresh(user)
#         return user
#     except IntegrityError:
#         await db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Cannot update: username or email already taken"
#         )
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An unexpected error occurred"
#         )