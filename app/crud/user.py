import random

from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> User:
    """
    Получает пользователя по его email.
    :param db: Сессия базы данных.
    :param email: Email пользователя.
    :return: :class:`User` Объект пользователя.
    """
    return db.query(User).filter(User.email == email).first()  # type: ignore


def create_user(db: Session, user: UserCreate) -> User:
    """
    Создаёт нового пользователя.
    :param db: Сессия базы данных.
    :param user: Данные для создания пользователя.
    :return: :class:`User` Созданный пользователь.
    """
    db_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def generate_confirmation_code(db: Session, email: str) -> str:
    """
    Генерирует и сохраняет код подтверждения для пользователя.
    :param db: Сессия базы данных.
    :param email: Email пользователя.
    :return: :class:`str` Сгенерированный код подтверждения.
    """
    code = str(random.randint(100000, 999999))
    db_user = get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.confirmation_code = code
    db.commit()
    db.refresh(db_user)
    return code
