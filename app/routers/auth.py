from app.controllers.auth_controller import AuthController
from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from fastapi import APIRouter
from app.schemas import UserResponse, TokenResponse, UserUpdateSchema
from app.crud import update_user


auth = AuthController()
router = APIRouter(prefix="/api/auth", tags=["Auth"])

router.post("/register", response_model=UserResponse)(auth.register)
router.get("/users", response_model=list[UserResponse])(auth.all_users)
router.post("/login", response_model=TokenResponse)(auth.login)
router.get("/user/me", response_model=UserResponse)(auth.me)
router.post("/refresh")(auth.refresh)

@router.put("/user-update/{user_id}", response_model=UserResponse)
async def UserUpdate(user_id: int, user_update: UserUpdateSchema, db: AsyncSession = Depends(get_db)):
    update_data = user_update.model_dump(exclude_unset=True)
    updated_user = await update_user(db, user_id, update_data)

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return updated_user
