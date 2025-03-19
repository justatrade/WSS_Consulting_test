import random

from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()  # type: ignore

def create_user(db: Session, user: UserCreate):
    db_user = User(
        email=user.email, hashed_password = get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def generate_confirmation_code(db: Session, email: str):
    code = str(random.randint(100000, 999999))
    db_user = get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.confirmation_code = code
    db.commit()
    db.refresh(db_user)
    return code