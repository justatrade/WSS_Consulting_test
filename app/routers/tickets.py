from typing import Dict, List, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.crud.ticket import (
    create_ticket,
    delete_ticket,
    get_ticket,
    get_tickets,
    update_ticket,
)
from app.db.session import get_db
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketInDB, TicketUpdate

router = APIRouter()


@router.post("/", response_model=TicketInDB)
def create_new_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TicketInDB:
    """
    Создаёт новую заявку.
    :param ticket: Данные для создания заявки.
    :param db: Сессия базы данных.
    :param current_user: Текущий пользователь.
    :return: :class:`TicketInDB` Созданная заявка.
    """
    return create_ticket(db=db, ticket=ticket, owner_id=current_user.id)


@router.get("/", response_model=Dict[str, Union[List[TicketInDB], int]])
def read_tickets(
    skip: int = Query(0, description="Сколько записей пропустить"),
    limit: int = Query(100, description="Лимит записей на странице"),
    sort_by: str = Query(
        "created_at", description="Поле для сортировки (created_at, title)"
    ),
    order: str = Query("desc", description="Порядок сортировки (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Union[List[TicketInDB], int]]:
    """
    Возвращает список заявок с пагинацией и сортировкой.
    :param skip: Количество пропускаемых записей.
    :param limit: Лимит записей на странице.
    :param sort_by: Поле для сортировки (created_at или title).
    :param order: Порядок сортировки (asc или desc).
    :param db: Сессия базы данных.
    :param current_user: Текущий пользователь.
    :return: Словарь с заявками и метаданными пагинации.
    """
    tickets = get_tickets(
        db=db,
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )
    total = (
        db.query(Ticket).filter(Ticket.owner_id == current_user.id).count()
    )  # type:ignore
    return {"tickets": tickets, "total": total, "skip": skip, "limit": limit}


@router.get("/{ticket_id}", response_model=TicketInDB)
def read_ticket(ticket_id: int, db: Session = Depends(get_db)) -> TicketInDB:
    """
    Получает заявку по её ID.
    :param ticket_id: ID заявки.
    :param db: Сессия базы данных.
    :return: :class:`TicketInDB` Объект заявки.
    """
    db_ticket = get_ticket(db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db_ticket


@router.put("/{ticket_id}", response_model=TicketInDB)
def update_existing_ticket(
    ticket_id: int,
    ticket: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TicketInDB:
    """
    Обновляет данные заявки.
    :param ticket_id: ID заявки.
    :param ticket: Данные для обновления заявки.
    :param db: Сессия базы данных.
    :param current_user: Текущий пользователь.
    :return: :class:`TicketInDB` Обновлённая заявка.
    """
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
    current_user: User = Depends(get_current_user),
) -> TicketInDB:
    """
    Закрывает заявку.
    :param ticket_id: ID заявки.
    :param db: Сессия базы данных.
    :param current_user: Текущий пользователь.
    :return: :class:`TicketInDB` Закрытая заявка.
    """
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
    current_user: User = Depends(get_current_user),
) -> TicketInDB:
    """
    Удаляет заявку по её ID.
    :param ticket_id: ID заявки.
    :param db: Сессия базы данных.
    :param current_user: Текущий пользователь.
    :return: :class:`TicketInDB` Удалённая заявка.
    """
    db_ticket = get_ticket(db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if db_ticket.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return delete_ticket(db=db, ticket_id=ticket_id)
