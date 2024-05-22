from fastapi import APIRouter, Query

from starlette import status

from src.admin.crud import filtered_users, sorted_users
from src.auth.schemas.user import UsersResponseSchema


router = APIRouter(prefix="/admin", tags=["admin"])  # include_in_schema=False


@router.get(
    "/users/",
    response_model=UsersResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": UsersResponseSchema}},
)
async def get_users(
    id: int = Query(None, description="User ID"),
    email: str = Query(None, description="User Email"),
    is_active: bool = Query(None, description="User Active Status"),
):
    users = await filtered_users(id, email, is_active)
    return {"users": users}


@router.get(
    "/sort-users/",
    response_model=UsersResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": UsersResponseSchema}},
)
async def get_sorted_users(
    created_at: bool = Query(None, description="Created At"),
    is_active: bool = Query(None, description="User Active Status"),
    desc: bool = Query(False, description="Sort Desc"),
):
    users = await sorted_users(created_at, is_active, desc)
    return {"users": users}
