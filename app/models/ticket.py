from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="open")
    owner_id = Column(Integer, ForeignKey("users.id"))
    # pylint: disable=E1102
    created_at = Column(DateTime(timezone=True), server_default=func.now())
