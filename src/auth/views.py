from fastapi import (
    APIRouter,
    Body,
    Depends
)

from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import create_user, get_user_by_email
from auth.dependecies import get_current_user, http_bearer
from auth.exceptions import (
    credential_exceptions,
    not_active_user_exception,
    repeat_email_exception,
)
from auth.schemas.token import TokenSchema
from auth.schemas.user import (
    ChangePasswordSchema,
    UserCreationSchema,
    UserLoginSchema,
    UserSchema
)
from auth.utils.my_jwt import create_access_token, create_refresh_token
from auth.utils.password import hash_password, verify_password
from db.main import get_session
from models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[Depends(http_bearer)],
)


@router.post("/signup", response_model=UserSchema)
async def signup(
    payload: UserCreationSchema = Body(),
    session: AsyncSession = Depends(get_session),
) -> UserSchema:
    if (
        await get_user_by_email(session=session, email=payload.email)
        is not None
    ):
        raise repeat_email_exception

    payload.password = hash_password(payload.password)
    return await create_user(user_data=payload, session=session)


@router.post("/login", response_model=TokenSchema)
async def login(
    payload: UserLoginSchema = Body(),
    session: AsyncSession = Depends(get_session),
) -> TokenSchema:
    user = await get_user_by_email(session=session, email=payload.email)
    if user is None or not verify_password(payload.password, user.password):
        raise credential_exceptions

    if not user.is_active:
        raise not_active_user_exception

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return TokenSchema(access_token=access_token, refresh_token=refresh_token)


@router.post("/change-password", response_model=UserSchema)
async def change_password(
    payload: ChangePasswordSchema,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserSchema:
    if not verify_password(payload.old_password, user.password):
        raise credential_exceptions
    new_password = hash_password(payload.new_password)

    user.password = new_password
    await session.commit()
    await session.refresh(user)
    return UserSchema(**user.__dict__)
