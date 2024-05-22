from fastapi import HTTPException

from starlette import status

negative_balance_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Balance cannot be negative",
)

insufficient_balance_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Insufficient funds on the balance sheet",
)
