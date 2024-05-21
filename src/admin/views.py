from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBearer

from starlette import status

from admin.crud import filtered_users, sorted_users
from auth.schemas.user import UsersResponseSchema
from db.session import handle_session

http_bearer = HTTPBearer(auto_error=False)

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(http_bearer), Depends(handle_session)],
    # include_in_schema=False
)


@admin_router.get(
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


@admin_router.get(
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
