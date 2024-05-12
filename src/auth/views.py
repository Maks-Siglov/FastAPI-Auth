from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from auth.crud import create_user, get_user_by_email
from auth.dependencies import (
    get_current_user,
    get_token_payload,
    get_user_from_refresh_token,
    http_bearer
)
from auth.exceptions import (
    credential_exceptions,
    not_active_user_exception,
    repeat_email_exception
)
from auth.schemas.token import (
    AccessTokenSchema,
    RevokedAccessTokenSchema,
    TokenSchema
)
from auth.schemas.user import (
    ChangePasswordSchema,
    UserCreationSchema,
    UserLoginSchema,
    UserSchema
)
from auth.utils.my_jwt import (
    create_access_token,
    create_refresh_token,
    revoke_jwt
)
from auth.utils.password import hash_password, verify_password
from db.session import handle_session, s
from models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[Depends(http_bearer), Depends(handle_session)],
)


@router.post("/signup", response_model=UserSchema)
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


@router.post("/login/", response_model=TokenSchema)
async def login(
    payload: UserLoginSchema = OAuth2PasswordRequestForm,
) -> TokenSchema:
    user = await get_user_by_email(email=payload.email)
    if user is None or not verify_password(payload.password, user.password):
        raise credential_exceptions

    if not user.is_active:
        raise not_active_user_exception

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return TokenSchema(access_token=access_token, refresh_token=refresh_token)


@router.post("/change-password/", response_model=UserSchema)
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


@router.post("/logout/", response_model=RevokedAccessTokenSchema)
async def logout(
    payload: dict[str, Any] = Depends(get_token_payload),
) -> RevokedAccessTokenSchema:
    revoked_token = revoke_jwt(payload)
    return RevokedAccessTokenSchema(access_token=revoked_token)


@router.post("/refresh/", response_model=AccessTokenSchema)
async def refresh_access_token(
    user: User = Depends(get_user_from_refresh_token),
) -> AccessTokenSchema:
    access_token = create_access_token(user)
    return AccessTokenSchema(access_token=access_token)


@router.post("/deactivate/")
async def deactivate_user(user: User = Depends(get_current_user)):
    user.is_active = False
    await s.user_db.commit()
    await s.user_db.refresh(user)
    return UserSchema(**user.__dict__)


@router.get("/")
async def protect_test(user: User = Depends(get_current_user)):
    return {"message": f"Hi {user.email}"}
