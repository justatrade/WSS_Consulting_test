from typing import Dict, List, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.crud.ticket import (
    get_ticket, get_tickets, create_ticket, update_ticket, delete_ticket
)
from app.db.session import get_db
from app.models.user import User
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketInDB


router = APIRouter()

@router.post("/", response_model=TicketInDB)
def create_new_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_ticket(db=db, ticket=ticket, owner_id=current_user.id)

@router.get("/", response_model=Dict[str, Union[List[TicketInDB], int]])
def read_tickets(
        skip: int = Query(0, description="Сколько записей пропустить"),
        limit: int = Query(100, description="Лимит записей на странице"),
        sort_by: str = Query("created_at", description="Поле для сортировки (created_at, title)"),
        order: str = Query("desc", description="Порядок сортировки (asc, desc)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    tickets = get_tickets(
        db=db,
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order
    )
    total = db.query(Ticket).filter(Ticket.owner_id == current_user.id).count()  # type:ignore
    return {
        "tickets": tickets,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{ticket_id}", response_model=TicketInDB)
def read_ticket(ticket_id: int, db: Session = Depends(get_db)):
    db_ticket = get_ticket(db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db_ticket

@router.put("/{ticket_id}", response_model=TicketInDB)
def update_existing_ticket(
    ticket_id: int,
    ticket: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_ticket = get_ticket(db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if db_ticket.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return update_ticket(db=db, ticket_id=ticket_id, ticket=ticket)

@router.patch("/tickets/{ticket_id}/close", response_model=TicketInDB)
def close_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_ticket = get_ticket(db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if db_ticket.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return update_ticket(
        db=db, ticket_id=ticket_id, ticket=TicketUpdate(status="closed")
    )

@router.delete("/{ticket_id}", response_model=TicketInDB)
def delete_existing_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_ticket = get_ticket(db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if db_ticket.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return delete_ticket(db=db, ticket_id=ticket_id)
