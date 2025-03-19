from datetime import datetime, timedelta
from passlib.context import CryptContext

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token


SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days
oauth2_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_token(token: Token) -> str:
    if token.type == "access":
        expires = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    elif token.type == "refresh":
        expires = datetime.now() + timedelta(days=7)
    else:
        expires = datetime.now()
    token.exp = expires
    return jwt.encode(token.model_dump(), SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.exceptions.PyJWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = decode_token(token)
        email: str = payload.get("sub")
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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = decode_token(token)
        email: str = payload.get("sub")
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
