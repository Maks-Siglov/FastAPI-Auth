from fastapi import APIRouter, Depends

from starlette import status

from src.api.v1.admin.crud import filtered_users
from src.api.v1.admin.dependencies import check_admin_role
from src.api.v1.admin.models.admin_query_params import AdminQueryParams
from src.api.v1.auth.models.user import UserResponseSchema, UsersResponseSchema

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(check_admin_role)],
)  # include_in_schema=False


@router.get(
    "/users/",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": UsersResponseSchema}},
)
async def get_users(
    params: AdminQueryParams = Depends(AdminQueryParams),
) -> dict[str, list[UserResponseSchema]]:
    users = await filtered_users(params)
    return {
        "users": [UserResponseSchema.model_validate(user) for user in users]
    }
