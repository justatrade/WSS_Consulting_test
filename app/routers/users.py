from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.crud.user import (
    create_user,
    get_user_by_email,
    generate_confirmation_code
)
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB
from app.services.email import send_email


router = APIRouter()

@router.post("/register", response_model=UserInDB)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_created = create_user(db=db, user=user)
    code = generate_confirmation_code(db, email=user.email)
    await send_email(
        to=user.email,
        subject="Confirm your registration",
        body=f"Your confirmation code is {code}."
    )
    return user_created


@router.get("/users/me", response_model=UserInDB)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
