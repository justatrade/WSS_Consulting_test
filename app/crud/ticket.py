from fastapi import HTTPException, status

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST

from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketInDB


def get_ticket(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()  # type:ignore

def get_tickets(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    order: str = "desc"
) -> list[TicketInDB]:
    if sort_by == "title":
        sort_field = Ticket.title
    elif sort_by == "created_at":
        sort_field = Ticket.created_at
    else:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="sort_by must be 'created_at' or 'title'",
        )

    if order == "asc":
        sort_order = asc(sort_field)
    elif order == "desc":
        sort_order = desc(sort_field)
    else:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="order must be 'asc' or 'desc'",
        )

    return (
        db.query(Ticket)
        .filter(Ticket.owner_id == owner_id)  # type:ignore
        .order_by(sort_order)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_ticket(db: Session, ticket: TicketCreate, owner_id: int):
    db_ticket = Ticket(**ticket.model_dump(), owner_id=owner_id)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def update_ticket(db: Session, ticket_id: int, ticket: TicketUpdate):
    db_ticket = get_ticket(db, ticket_id=ticket_id)
    if not db_ticket:
        return None
    for key, value in ticket.model_dump(exclude_unset=True).items():
        setattr(db_ticket, key, value)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def delete_ticket(db: Session, ticket_id: int):
    db_ticket = get_ticket(db, ticket_id=ticket_id)
    if not db_ticket:
        return None
    db.delete(db_ticket)
    db.commit()
    return db_ticket