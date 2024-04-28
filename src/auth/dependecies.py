from fastapi import Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import get_user_by_email
from auth.exceptions import invalid_token_error
from auth.utils import decode_jwt
from db.main import get_session
from models import User

http_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")


def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_jwt(token)
    except InvalidTokenError as e:
        raise invalid_token_error
    return payload


async def get_current_user(
    payload: dict = Depends(get_token_payload),
    session: AsyncSession = Depends(get_session),
) -> User:
    if (email := payload.get("sub")) is None:

        raise invalid_token_error
    if (user := await get_user_by_email(session=session, email=email)) is None:
        raise invalid_token_error

    return user
