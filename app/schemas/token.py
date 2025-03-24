from datetime import datetime

from pydantic import BaseModel


class TokenBase(BaseModel):
    type: str
    sub: str


class TokenCreate(TokenBase):
    exp: datetime
