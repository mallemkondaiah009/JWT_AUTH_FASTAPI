from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserResponse, TokenResponse, LoginRequest
from app.crud import create_user, get_users, get_user_by_email
from app.database import get_db
from app.security import verify_password, create_access_token
from fastapi import HTTPException, status

router = APIRouter(prefix='/api/auth')

@router.post('/register', response_model=UserResponse)
def UserRegisteration(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.get('/users', response_model=list[UserResponse])
def AllUsers(db: Session = Depends(get_db)):
    return get_users(db)

@router.post("/login", response_model=TokenResponse)
def UserLogin(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": db_user.email})
    return {"access_token": token}




