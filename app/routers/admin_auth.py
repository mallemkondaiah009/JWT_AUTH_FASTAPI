from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID


from app.database import get_db
from app.dependencies import get_current_user, admin_required
from app.schemas import (
    AdminCreate,
    UserCreate,
)
from app.crud import (
    create_admin,
    get_users,
    get_user_by_id,
    update_user,
    deactivate_user,
    create_user,
)

router = APIRouter(prefix='/api/auth', tags=['Admin Auth'])


@router.post("/admin/create", status_code=201)
async def create_admin_user( data: AdminCreate, db: AsyncSession = Depends(get_db), admin=Depends(admin_required)):
    admin = await create_admin(db, data)
    return {
        "message": "Admin created successfully",
        "admin_id": admin.id
    }


@router.get("/users", status_code=200)
async def list_users(db: AsyncSession = Depends(get_db),admin=Depends(admin_required)):
    return await get_users(db)

@router.get("/users/{user_id}")
async def get_users(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(admin_required)
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def admin_post_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(admin_required)
):
    user = await create_user(db, data)

    return {
        "message": "User created successfully by admin",
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at":user.created_at
    }

@router.patch("/users/{user_id}")
async def admin_update_user(
    user_id: UUID,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    admin=Depends(admin_required)
):
    return await update_user(db, user_id, update_data)


@router.delete("/users/{user_id}")
async def admin_deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(admin_required)
):
    return await deactivate_user(db, user_id)
