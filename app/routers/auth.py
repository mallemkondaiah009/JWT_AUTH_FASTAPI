from app.controllers.auth_controller import AuthController
from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from fastapi import APIRouter, Path
from app.schemas import UserResponse, TokenResponse, UserUpdateSchema
from app.crud import update_user, delete_user
from uuid import UUID


auth = AuthController()
router = APIRouter(prefix="/api/auth", tags=["Auth"])

router.post("/register", response_model=UserResponse)(auth.register)
router.get("/users", response_model=list[UserResponse])(auth.all_users)
router.post("/login", response_model=TokenResponse)(auth.login)
router.get("/user/me", response_model=UserResponse)(auth.me)
router.post("/refresh")(auth.refresh)

@router.put("/user-update/{user_id}", response_model=UserResponse)  
async def UpdateUser(
    user_id: UUID, 
    user_update: UserUpdateSchema = Depends(),
    db: AsyncSession = Depends(get_db)
):
    update_data = user_update.model_dump(
        exclude_unset=True,   # Only fields sent by client
        exclude_none=True     # Skip fields that became None (including from empty strings)
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid data provided for update"
        )

    return await update_user(db, user_id, update_data)

@router.delete('/delete-user/{user_id}')
async def DeleteUser(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await delete_user(db, user_id)
