import asyncio
import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends

from redis.asyncio import Redis
from starlette import status

from src.api.exceptions import (
    BLOCKED_USER_EXCEPTION,
    CREDENTIAL_EXCEPTIONS,
    NOT_ACTIVE_USER_EXCEPTION,
    REPEAT_EMAIL_EXCEPTION,
)
from src.api.v1.users.crud import (
    activate_user,
    change_user_password,
    create_user,
    deactivate_my_user,
    delete_my_user,
    edit_user,
    get_user_by_email,
)
from src.api.v1.users.dependencies import (
    get_current_user,
    get_redis_client,
    get_token_payload,
    get_user_from_refresh_token,
)
from src.api.v1.users.models.token import (
    AccessTokenSchema,
    RevokedAccessTokenSchema,
    TokenSchema,
)
from src.api.v1.users.models.user import (
    ChangePasswordSchema,
    DeactivateUserSchema,
    DeleteUserSchema,
    UserCreationSchema,
    UserLoginSchema,
    UserResponseSchema,
    UserSchema,
)
from src.api.v1.users.utils.my_jwt import (
    create_access_token,
    create_refresh_token,
    revoke_jwt,
)
from src.api.v1.users.utils.password import hash_password, verify_password
from src.db.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/signup/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"model": UserResponseSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": REPEAT_EMAIL_EXCEPTION.detail
        },
    },
)
async def signup(payload: UserCreationSchema) -> UserResponseSchema:
    if (user := await get_user_by_email(email=payload.email)) is not None:
        if user.is_active:
            raise REPEAT_EMAIL_EXCEPTION

        await activate_user(user)
        return UserResponseSchema.model_validate(user)

    payload.password = hash_password(payload.password)
    user = await create_user(user_data=payload)
    return UserResponseSchema.model_validate(user)


@router.post(
    "/login/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": TokenSchema},
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid credentials or user is not active"
        },
    },
)
async def login(
    payload: UserLoginSchema,
    redis_client: Redis = Depends(get_redis_client),
) -> TokenSchema:
    user = await get_user_by_email(email=payload.email)
    if user is None or not verify_password(payload.password, user.password):
        raise CREDENTIAL_EXCEPTIONS

    if not user.is_active:
        raise NOT_ACTIVE_USER_EXCEPTION

    if user.is_blocked:
        raise BLOCKED_USER_EXCEPTION

    access_token, access_payload = create_access_token(user)
    refresh_token, refresh_payload = create_refresh_token(user)

    now = int(datetime.utcnow().timestamp())
    await asyncio.gather(
        redis_client.set(
            name=access_token,
            value=json.dumps(access_payload),
            ex=int(access_payload["exp"]) - now,
        ),
        redis_client.set(
            name=refresh_token,
            value=json.dumps(refresh_payload),
            ex=int(refresh_payload["exp"]) - now,
        ),
    )

    return TokenSchema(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/logout/",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": RevokedAccessTokenSchema}},
)
async def logout(
    payload: dict[str, Any] = Depends(get_token_payload),
) -> RevokedAccessTokenSchema:
    revoked_token = revoke_jwt(payload)
    return RevokedAccessTokenSchema(access_token=revoked_token)


@router.post(
    "/refresh/",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_201_CREATED: {"model": AccessTokenSchema}},
)
async def refresh_access_token(
    user: User = Depends(get_user_from_refresh_token),
) -> AccessTokenSchema:
    access_token, _ = create_access_token(user)
    return AccessTokenSchema(access_token=access_token)


@router.post(
    "/deactivate/",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": DeactivateUserSchema}},
)
async def deactivate_user(
    user: User = Depends(get_current_user),
) -> DeactivateUserSchema:
    await deactivate_my_user(user)
    return DeactivateUserSchema.model_validate(user)


@router.post(
    "/delete/",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": DeleteUserSchema}},
)
async def delete_user(
    user: User = Depends(get_current_user),
) -> DeleteUserSchema:
    await delete_my_user(user)
    return DeleteUserSchema.model_validate(user)


@router.get(
    path="/me/",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": UserResponseSchema}},
)
async def get_user(
    user: User = Depends(get_current_user),
) -> UserResponseSchema:
    return UserResponseSchema.model_validate(user)


@router.patch(
    "/change-password/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": UserResponseSchema},
        status.HTTP_401_UNAUTHORIZED: {
            "description": CREDENTIAL_EXCEPTIONS.detail
        },
    },
)
async def change_password(
    payload: ChangePasswordSchema,
    user: User = Depends(get_current_user),
) -> UserResponseSchema:
    if not verify_password(payload.old_password, user.password):
        raise CREDENTIAL_EXCEPTIONS

    new_password = hash_password(payload.new_password)
    await change_user_password(user, new_password)
    return UserResponseSchema.model_validate(user)


@router.put(
    path="/update/",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": UserResponseSchema}},
)
async def update_user(
    payload: UserSchema,
    user: User = Depends(get_current_user),
) -> UserResponseSchema:
    await edit_user(user, payload.model_dump(exclude_none=True))
    return UserResponseSchema.model_validate(user)
