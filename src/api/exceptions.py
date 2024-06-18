from fastapi import HTTPException

from starlette import status

credential_exceptions = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid user credentials",
)


not_active_user_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User is not active",
)


repeat_email_exception = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Email already exists",
)


invalid_token_exception = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"},
)


invalid_token_credential_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Invalid token credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


invalid_token_type_exception = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Invalid token type",
    headers={"WWW-Authenticate": "Bearer"},
)

revoked_token_error = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Token has been revoked",
    headers={"WWW-Authenticate": "Bearer"},
)


unable_decode_jwt_exception = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Unable to decode JWT",
    headers={"WWW-Authenticate": "Bearer"},
)

invalid_user_cache_id_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User cache id is invalid",
    headers={"WWW-Authenticate": "Bearer"},
)

negative_balance_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Balance cannot be negative",
)

insufficient_balance_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Insufficient funds on the balance sheet",
)


not_admin_user_role_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="User do not has admin role",
)
