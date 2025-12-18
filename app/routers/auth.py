from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserResponse, TokenResponse, LoginRequest
from app.crud import create_user, get_users, get_user_by_email
from app.database import get_db
from app.security import verify_password, create_access_token
from fastapi import HTTPException, status
from app.dependencies import get_current_user

router = APIRouter(prefix='/api/auth')

@router.post('/register', response_model=UserResponse)
def UserRegisteration(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.get('/users', response_model=list[UserResponse])
def AllUsers(db: Session = Depends(get_db)):
    return get_users(db)

@router.post("/login", response_model=TokenResponse)
def UserLogin(user: LoginRequest, response: Response, db: Session = Depends(get_db)):
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

    access_token = create_access_token({"sub": db_user.email})

    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=1800 #30 minutes
    )

    return {"access_token": access_token}


@router.get("/user/me", response_model = UserResponse)
def get_me(current_user = Depends(get_current_user)):
    return current_user



