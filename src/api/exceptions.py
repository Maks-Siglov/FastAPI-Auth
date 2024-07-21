from fastapi import HTTPException

from starlette import status

CREDENTIAL_EXCEPTIONS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid user credentials",
)

NOT_ACTIVE_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User is not active",
)


BLOCKED_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Account is blocked",
)

REPEAT_EMAIL_EXCEPTION = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Email already exists",
)

INVALID_TOKEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"},
)

INVALID_TOKEN_CREDENTIAL_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Invalid token credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

INVALID_TOKEN_TYPE_EXCEPTION = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Invalid token type",
    headers={"WWW-Authenticate": "Bearer"},
)

UNABLE_DECODE_JWT_EXCEPTION = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Unable to decode JWT",
    headers={"WWW-Authenticate": "Bearer"},
)

INVALID_USER_CACHE_ID_EXCEPTION = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User cache id is invalid",
    headers={"WWW-Authenticate": "Bearer"},
)

REVOKED_TOKEN_ERROR = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Token has been revoked",
    headers={"WWW-Authenticate": "Bearer"},
)

NEGATIVE_BALANCE_ERROR = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Balance cannot be negative",
)

INSUFFICIENT_BALANCE_ERROR = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Insufficient funds on the balance sheet",
)

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Not found",
)

ALREADY_BLOCKED_EXCEPTION = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User already blocked",
)


NOT_BLOCKED_EXCEPTION = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User not blocked",
)


ADMIN_BLOCK_ITSELF_EXCEPTION = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Admin cannot block itself",
)
