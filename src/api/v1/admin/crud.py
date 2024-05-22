from sqlalchemy import Result, Row, select

from src.db.models import User
from src.db.session import s


async def filtered_users(
    id: int | None, email: str | None, is_active: bool | None
) -> Result[Row[User]]:
    query = select(User)
    if id is not None:
        query = query.where(User.id == id)
    elif email is not None:
        query = query.where(User.email == email)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    return await s.user_db.execute(query)


async def sorted_users(
    is_active: bool | None, created_at: bool | None, desc: bool
) -> Result[Row[User]]:
    query = select(User)

    if created_at is not None:
        query = query.order_by(
            User.created_at.desc() if desc else User.created_at
        )
    elif is_active is not None:
        query = query.order_by(
            User.is_active.desc() if desc else User.is_active
        )
    else:
        query = query.order_by(User.id.desc() if desc else User.id)

    return await s.user_db.execute(query)