from fastapi import APIRouter, Query

from starlette import status

from src.api.v1.admin.crud import filtered_users
from src.api.v1.auth.schemas.user import UsersResponseSchema

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
    order_by: str | None = Query(None, description="User Order by"),
    desc: bool | None = Query(None, description="User descending order by"),
):
    users = await filtered_users(user_id, email, is_active, order_by, desc)
    return {"users": users}
