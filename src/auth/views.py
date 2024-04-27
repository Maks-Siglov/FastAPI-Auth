from fastapi import (
    APIRouter,
    Body,
    Depends
)

from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import create_user, get_user_by_email
from auth.exceptions import credential_exceptions, not_active_user_exceptions
from auth.schemas.token import TokenSchema
from auth.schemas.user import (
    UserCreationSchema,
    UserLoginSchema,
    UserSchema
)
from auth.utils import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password
)
from db.main import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserSchema)
async def signup(
    payload: UserCreationSchema = Body(),
    session: AsyncSession = Depends(get_session),
) -> UserSchema:
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
        raise not_active_user_exceptions

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return TokenSchema(access_token=access_token, refresh_token=refresh_token)
