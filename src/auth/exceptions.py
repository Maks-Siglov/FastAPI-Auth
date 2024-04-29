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
)


invalid_token_credential_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Invalid token credentials",
)


revoked_token_error = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Token has been revoked",
)


unable_decode_jwt_exception = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Unable to decode JWT",
)
