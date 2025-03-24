from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketInDB, TicketUpdate


def get_ticket(db: Session, ticket_id: int) -> Ticket:
    """
    Получает заявку по её ID.
    :param db: Сессия базы данных.
    :param ticket_id: ID заявки.
    :return: :class:`Ticket` Объект заявки.
    """
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()  # type:ignore


def get_tickets(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    order: str = "desc",
) -> list[TicketInDB]:
    """
    Получает список заявок пользователя с пагинацией и сортировкой.
    :param db: Сессия базы данных.
    :param owner_id: ID владельца заявок.
    :param skip: Количество пропускаемых записей.
    :param limit: Лимит записей на странице.
    :param sort_by: Поле для сортировки (created_at или title).
    :param order: Порядок сортировки (asc или desc).
    :return: :class:`list[TicketInDB]` Список заявок.
    """
    if sort_by == "title":
        sort_field = Ticket.title
    elif sort_by == "created_at":
        sort_field = Ticket.created_at
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_by must be 'created_at' or 'title'",
        )

    if order == "asc":
        sort_order = asc(sort_field)
    elif order == "desc":
        sort_order = desc(sort_field)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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


def create_ticket(db: Session, ticket: TicketCreate, owner_id: int) -> Ticket:
    """
    Создаёт новую заявку.
    :param db: Сессия базы данных.
    :param ticket: Данные для создания заявки.
    :param owner_id: ID владельца заявки.
    :return: :class:`Ticket` Созданная заявка.
    """
    db_ticket = Ticket(**ticket.model_dump(), owner_id=owner_id)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def update_ticket(db: Session, ticket_id: int, ticket: TicketUpdate) -> Ticket:
    """
    Обновляет данные заявки.
    :param db: Сессия базы данных.
    :param ticket_id: ID заявки.
    :param ticket: Данные для обновления заявки.
    :return: :class:`Ticket` Обновлённая заявка
    """
    db_ticket = get_ticket(db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for key, value in ticket.model_dump(exclude_unset=True).items():
        setattr(db_ticket, key, value)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def delete_ticket(db: Session, ticket_id: int) -> Ticket:
    """
    Удаляет заявку по её ID.
    :param db: Сессия базы данных.
    :param ticket_id: ID заявки.
    :return: :class:`Ticket` Удалённая заявка
    """
    db_ticket = get_ticket(db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(db_ticket)
    db.commit()
    return db_ticket
