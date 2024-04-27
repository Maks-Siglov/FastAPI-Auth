from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext

from core.settings import settings
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_jwt(token_type: str, token_data: dict, expire_time: int) -> str:
    jwt_payload = {"type": token_type}
    now = datetime.utcnow()
    jwt_payload["iat"] = now
    jwt_payload["exp"] = now + timedelta(minutes=expire_time)

    jwt_payload.update(token_data)
    return jwt.encode(
        payload=jwt_payload,
        algorithm=settings.security.ALGORITHM,
        key=settings.security.SECRET_KEY,
    )


def create_access_token(user: User) -> str:
    jwt_payload = {
        "sub": user.email,
        "id": user.id,
        "is_active": user.is_active,
    }
    return create_jwt(
        settings.jwt.ACCESS_TOKEN_TYPE,
        jwt_payload,
        settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def create_refresh_token(user: User) -> str:
    jwt_payload = {"sub": user.email}
    return create_jwt(
        settings.jwt.REFRESH_TOKEN_TYPE,
        jwt_payload,
        settings.jwt.REFRESH_TOKEN_EXPIRE_MINUTES,
    )


def decode_jwt(token: str | bytes):
    return jwt.decode(
        token=token,
        algorithm=settings.security.ALGORITHM,
        key=settings.security.SECRET_KEY,
    )
