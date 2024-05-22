from fastapi import APIRouter, Query

from sqlalchemy import Result, Row

from starlette import status

from src.api.v1.admin.crud import filtered_users, sorted_users
from src.api.v1.auth.schemas.user import UsersResponseSchema
from src.db.models import User

router = APIRouter(prefix="/admin", tags=["admin"])  # include_in_schema=False


@router.get(
    "/users/",
    response_model=UsersResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": UsersResponseSchema}},
)
async def get_users(
    user_id: int | None = Query(None, description="User ID"),
    email: str | None = Query(None, description="User Email"),
    is_active: bool | None = Query(None, description="User Active Status"),
) -> dict[str, Result[Row[User]]]:
    users = await filtered_users(user_id, email, is_active)
    return {"users": users}


@router.get(
    "/sort-users/",
    response_model=UsersResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": UsersResponseSchema}},
)
async def get_sorted_users(
    created_at: bool | None = Query(None, description="Created At"),
    is_active: bool | None = Query(None, description="User Active Status"),
    desc: bool | None = Query(False, description="Sort Desc"),
) -> dict[str, Result[Row[User]]]:
    users = await sorted_users(created_at, is_active, desc)
    return {"users": users}
