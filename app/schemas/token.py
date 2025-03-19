from pydantic import BaseModel


class Token(BaseModel):
    type: str
    sub: str
    exp: str = None
