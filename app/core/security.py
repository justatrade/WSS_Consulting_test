from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenBase, TokenCreate

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days
oauth2_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Хэширует пароль с использованием bcrypt.
    :param password: Пароль для хэширования.
    :return: :class:`str` Хэшированный пароль.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли пароль хэшу.
    :param plain_password: Пароль в открытом виде.
    :param hashed_password: Хэшированный пароль.
    :return: :class:`bool` True, если пароль совпадает с хэшем, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_token(token: TokenBase) -> str:
    """
    Создаёт JWT-токен на основе данных из модели TokenBase.
    :param token: Модель токена с данными для кодирования.
    :return: :class:`str` Модель токена с данными для кодирования.
    """
    if token.type == "access":
        expires = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    elif token.type == "refresh":
        expires = datetime.now() + timedelta(days=7)
    else:
        expires = datetime.now()

    token_create = TokenCreate(**token.model_dump(), exp=expires)

    return jwt.encode(token_create.model_dump(), SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, str]:
    """
    Декодирует JWT-токен и возвращает его payload.
    :param token:
    :return: :class:`dict` Payload токена, если декодирование успешно, иначе пустой словарь.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.exceptions.PyJWTError:
        return {}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Получает текущего пользователя по access-токену.
    :param credentials: Bearer-токен из заголовка Authorization.
    :param db: Сессия базы данных.
    :return: :class:`User` Объект текущего пользователя.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = decode_token(token)
        email = payload.get("sub", None)
        if email is None:
            raise credentials_exception
    except jwt.exceptions.PyJWTError:
        raise credentials_exception

    if payload.get("type", None) != "access":
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()  # type:ignore
    if user is None:
        raise credentials_exception
    return user


def get_current_refreshing_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Получает текущего пользователя по refresh-токену.
    :param credentials: Bearer-токен из заголовка Authorization.
    :param db: Сессия базы данных.
    :return: :class:`User` Объект текущего пользователя.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = decode_token(token)
        email = payload.get("sub", None)
        if email is None:
            raise credentials_exception
    except jwt.exceptions.PyJWTError:
        raise credentials_exception

    if payload.get("type", None) != "refresh":
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()  # type:ignore
    if user is None:
        raise credentials_exception
    return user
