from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.core.security import (
    create_token,
    decode_token,
    get_current_refreshing_user,
)
from app.crud.user import get_user_by_email, generate_confirmation_code
from app.db.session import get_db
from app.models.user import User
from app.services.email import send_email
from app.schemas.token import Token


router = APIRouter()

@router.post("/login")
async def login(email: EmailStr, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not registered",
        )
    code = generate_confirmation_code(db, email=email)
    await send_email(
        to=email,
        subject="Login code",
        body=f"Your login code is {code}."
    )
    return {"message": "Login code sent"}

@router.post("/confirm-login")
async def confirm_login(
        email: EmailStr, code: str, db: Session = Depends(get_db)
):
    db_user = get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not registered",
        )
    if db_user.confirmation_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid code",
        )
    db_user.confirmation_code = None
    db.commit()
    access_token = create_token(Token(type="access", sub=db_user.email))
    refreshing_token = create_token(Token(type="refresh", sub=db_user.email))
    return {
        "access_token": access_token,
        "refresh_token": refreshing_token,
        "token_type": "bearer",
    }

@router.post("/refresh-token")
async def refresh_token(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_refreshing_user)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = db.query(User).filter(User.email == current_user.email).first()  # type: ignore
    if user is None:
        raise credentials_exception

    access_token = create_token(Token(type="access", sub=user.email))
    return {"access_token": access_token, "token_type": "bearer"}
