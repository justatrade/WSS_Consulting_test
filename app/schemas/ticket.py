from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "open"

class TicketCreate(TicketBase):
    pass

class TicketUpdate(TicketBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class TicketInDB(TicketBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True