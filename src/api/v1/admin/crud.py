from sqlalchemy import ScalarResult, asc, desc, select

from src.api.v1.admin.models.admin_query_params import AdminQueryParams
from src.db.models import User
from src.db.session import s


async def filtered_users(params: AdminQueryParams) -> ScalarResult[User]:
    query = select(User)

    if params.user_id is not None:
        query = query.filter(User.id == params.user_id)
    if params.email is not None:
        query = query.filter(User.email == params.email)
    if params.first_name is not None:
        query = query.filter(User.first_name == params.first_name)
    if params.last_name is not None:
        query = query.filter(User.last_name == params.last_name)
    if params.is_active is not None:
        query = query.filter(User.is_active == params.is_active)
    if params.is_blocked is not None:
        query = query.filter(User.is_blocked == params.is_blocked)

    if params.order_by is not None and params.order_by in [
        "id",
        "balance",
        "updated_at",
    ]:
        order_func = desc if params.order_type == "desc" else asc
        query = query.order_by(order_func(getattr(User, params.order_by)))

    return await s.user_db.scalars(query)
