from sqlalchemy import desc, select

from src.db.models import User
from src.db.session import s


async def filtered_users(
    user_id: int | None,
    email: str | None,
    is_active: bool | None,
    order_by: str | None,
    order_desc: bool | None,
) -> list[User]:
    query = select(User)
    if user_id is not None:
        query = query.filter(User.id == user_id)
    elif email is not None:
        query = query.filter(User.email == email)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if order_by is not None and order_by in ["created_at", "is_active"]:
        if order_desc:
            query = query.order_by(desc(getattr(User, order_by)))
        else:
            query = query.order_by(getattr(User, order_by))

    result = await s.user_db.execute(query)
    return result.scalars().all()
