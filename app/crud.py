from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreate
from .security import hash_password


def create_user(db:Session, user:UserCreate):
    hashed_pwd = hash_password(user.password)

    user = User(
        username=user.username,
        email=user.email,
        password=hashed_pwd
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_users(db: Session):
    return db.query(User).all()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email==email).first()