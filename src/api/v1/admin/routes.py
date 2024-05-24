from fastapi import APIRouter, Depends

from starlette import status

from src.api.v1.admin.crud import filtered_users
from src.api.v1.admin.schemas import AdminQueryParams
from src.api.v1.auth.schemas.user import UsersResponseSchema

router = APIRouter(prefix="/admin", tags=["admin"])  # include_in_schema=False


@router.get(
    "/users/",
    response_model=UsersResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": UsersResponseSchema}},
)
async def get_users(params: AdminQueryParams = Depends(AdminQueryParams)):
    users = await filtered_users(params)
    return {"users": users}
