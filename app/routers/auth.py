from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.core.security import (
    create_token,
    get_current_refreshing_user,
    verify_password,
)
from app.crud.user import generate_confirmation_code, get_user_by_email
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenBase
from app.services.email import send_email

router = APIRouter()


@router.post(
    "/login",
    response_description="Сообщение об успешной отправке кода.",
)
async def login(
    email: EmailStr, password: str, db: Session = Depends(get_db)
) -> dict[str, str]:
    """
    Проверяет пароль и отправляет код подтверждения для входа на email пользователя.
    """
    db_user = get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not registered",
        )
    if not verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    code = generate_confirmation_code(db, email=email)
    await send_email(
        to=email, subject="Login code", body=f"Your login code is {code}."
    )
    return {"message": "Login code sent"}


@router.post(
    "/confirm-login",
    response_description="Access и refresh токены.",
)
async def confirm_login(
    email: EmailStr, code: str, db: Session = Depends(get_db)
) -> dict[str, str | dict[str, str]]:
    """
    Подтверждает вход по коду и возвращает access и refresh токены.
    """
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
    access_token = create_token(TokenBase(type="access", sub=db_user.email))
    refreshing_token = create_token(
        TokenBase(type="refresh", sub=db_user.email)
    )
    return {
        "access_token": access_token,
        "refresh_token": refreshing_token,
        "token_type": "bearer",
    }


@router.post(
    "/refresh-token",
    response_description="Новый access-токен.",
)
async def refresh_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_refreshing_user),
) -> dict[str, str]:
    """
    Обновляет access-токен с использованием refresh-токена.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = db.query(User).filter(User.email == current_user.email).first()  # type: ignore
    if user is None:
        raise credentials_exception

    access_token = create_token(TokenBase(type="access", sub=user.email))
    return {"access_token": access_token, "token_type": "bearer"}
