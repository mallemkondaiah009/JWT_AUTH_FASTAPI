from app.controllers.auth_controller import AuthController
from fastapi import APIRouter
from app.schemas import UserResponse, TokenResponse


auth = AuthController()
router = APIRouter(prefix="/api/auth", tags=["Auth"])

router.post("/register", response_model=UserResponse)(auth.register)
router.get("/users", response_model=list[UserResponse])(auth.all_users)
router.post("/login", response_model=TokenResponse)(auth.login)
router.get("/user/me", response_model=UserResponse)(auth.me)
router.post("/refresh")(auth.refresh)
