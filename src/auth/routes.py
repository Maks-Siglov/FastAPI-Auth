import json
import time
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from redis.asyncio import Redis
from starlette import status

from auth.crud import create_user, get_user_by_email
from auth.dependencies import (
    get_current_user,
    get_token_payload,
    get_user_from_refresh_token,
)
from auth.exceptions import (
    credential_exceptions,
    not_active_user_exception,
    repeat_email_exception,
)
from auth.schemas.token import (
    AccessTokenSchema,
    RevokedAccessTokenSchema,
    TokenSchema,
)
from auth.schemas.user import (
    ChangePasswordSchema,
    UserCreationSchema,
    UserLoginSchema,
    UserSchema,
)
from auth.utils.my_jwt import (
    create_access_token,
    create_refresh_token,
    revoke_jwt,
)
from auth.utils.password import hash_password, verify_password
from core.redis_config import get_redis_client
from db.session import s
from models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup/",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"model": UserSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": repeat_email_exception.detail
        },
    },
)
async def signup(
    payload: UserCreationSchema = OAuth2PasswordRequestForm,
) -> UserSchema:
    if (user := await get_user_by_email(email=payload.email)) is not None:
        if user.is_active:
            raise repeat_email_exception

        user.is_active = True
        await s.user_db.commit()
        await s.user_db.refresh(user)
        return UserSchema(**user.__dict__)

    payload.password = hash_password(payload.password)
    return await create_user(user_data=payload)


@router.post(
    "/login/",
    response_model=None,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": TokenSchema},
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid credentials or user is not active"
        },
    },
)
async def login(
    payload: UserLoginSchema = OAuth2PasswordRequestForm,
    redis_client: Redis = Depends(get_redis_client),
) -> TokenSchema:
    user = await get_user_by_email(email=payload.email)
    if user is None or not verify_password(payload.password, user.password):
        raise credential_exceptions

    if not user.is_active:
        raise not_active_user_exception

    access_token, access_payload = create_access_token(user)
    refresh_token, refresh_payload = create_refresh_token(user)

    now = int(time.time())
    await redis_client.set(
        name=access_token,
        value=json.dumps(access_payload),
        ex=access_payload["exp"] - now,
    )
    await redis_client.set(
        name=refresh_token,
        value=json.dumps(refresh_payload),
        ex=refresh_payload["exp"] - now,
    )

    return TokenSchema(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/change-password/",
    response_model=None,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": UserSchema},
        status.HTTP_401_UNAUTHORIZED: {
            "description": credential_exceptions.detail
        },
    },
)
async def change_password(
    payload: ChangePasswordSchema,
    user: User = Depends(get_current_user),
) -> UserSchema:
    if not verify_password(payload.old_password, user.password):
        raise credential_exceptions
    new_password = hash_password(payload.new_password)

    user.password = new_password
    await s.commit()
    await s.refresh(user)
    return UserSchema(**user.__dict__)


@router.post(
    "/logout/",
    response_model=None,
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
    response_model=None,
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
    response_model=None,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": UserSchema}},
)
async def deactivate_user(
    user: User = Depends(get_current_user),
) -> UserSchema:
    user.is_active = False
    await s.user_db.commit()
    await s.user_db.refresh(user)
    return UserSchema(**user.__dict__)