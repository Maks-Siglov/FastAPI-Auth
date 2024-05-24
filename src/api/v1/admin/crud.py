from sqlalchemy import desc, select

from src.api.v1.admin.schemas import AdminQueryParams
from src.db.models import User
from src.db.session import s


async def filtered_users(params: AdminQueryParams) -> list[User]:
    query = select(User)
    if params.user_id is not None:
        query = query.filter(User.id == params.user_id)
    elif params.email is not None:
        query = query.filter(User.email == params.email)
    if params.is_active is not None:
        query = query.filter(User.is_active == params.is_active)

    if params.order_by is not None and params.order_by in [
        "created_at",
        "is_active",
    ]:
        if params.desc:
            query = query.order_by(desc(getattr(User, params.order_by)))
        else:
            query = query.order_by(getattr(User, params.order_by))

    result = await s.user_db.execute(query)
    return result.scalars().all()
