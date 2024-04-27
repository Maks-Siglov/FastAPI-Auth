from fastapi import (
    APIRouter,
    Body,
    Depends,
)

from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import create_user
from auth.schemas import UserCreationSchema, UserSchema
from auth.utils import hash_password

from db.main import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserSchema)
async def signup(
    payload: UserCreationSchema = Body(),
    session: AsyncSession = Depends(get_session),
) -> UserSchema:
    payload.password = hash_password(payload.password)
    return await create_user(user_data=payload, session=session)
