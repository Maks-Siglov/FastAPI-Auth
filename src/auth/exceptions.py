from fastapi import HTTPException

from starlette import status

credential_exceptions = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid user credentials",
)


not_active_user_exceptions = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User is not active",
)
