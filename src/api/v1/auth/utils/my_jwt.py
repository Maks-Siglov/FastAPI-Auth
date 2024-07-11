from datetime import datetime
from typing import Any

import jwt

from src.db.models import User
from src.settings import JWTSettings, SecuritySettings


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_time_seconds: int,
) -> tuple[str, dict[str, Any]]:
    jwt_payload = {"type": token_type}
    now = int(datetime.utcnow().timestamp())
    jwt_payload["iat"] = str(now)
    jwt_payload["exp"] = str(now + expire_time_seconds)

    jwt_payload.update(token_data)
    token = jwt.encode(
        payload=jwt_payload,
        algorithm=SecuritySettings.ALGORITHM,
        key=SecuritySettings.SECRET_KEY,
    )

    return token, jwt_payload


def create_access_token(user: User) -> tuple[str, dict[str, Any]]:
    jwt_payload = {
        "sub": user.email,
        "id": user.id,
        "is_active": user.is_active,
        "token_revoked": False,
    }
    return create_jwt(
        JWTSettings.ACCESS_TOKEN_TYPE,
        jwt_payload,
        JWTSettings.ACCESS_TOKEN_EXPIRE_SECONDS,
    )


def create_refresh_token(user: User) -> tuple[str, dict[str, Any]]:
    jwt_payload = {"sub": user.email, "token_revoked": False}
    return create_jwt(
        JWTSettings.REFRESH_TOKEN_TYPE,
        jwt_payload,
        JWTSettings.REFRESH_TOKEN_EXPIRE_SECONDS,
    )


def revoke_jwt(payload: dict[str, Any]) -> str:
    payload["token_revoked"] = True
    return jwt.encode(
        payload=payload,
        algorithm=SecuritySettings.ALGORITHM,
        key=SecuritySettings.SECRET_KEY,
    )


def decode_jwt(token: bytes) -> dict[str, Any]:
    return jwt.decode(
        jwt=token,
        algorithms=[SecuritySettings.ALGORITHM],
        key=SecuritySettings.SECRET_KEY,
        options={"verify_exp": False},
    )


def validate_token_type(payload: dict[str, Any], token_type: str) -> bool:
    return payload.get("type") == token_type
