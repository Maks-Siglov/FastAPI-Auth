from fastapi import APIRouter, Body

from auth.crud import create_user
from auth.schemas import UserCreationSchema, UserSchema
from auth.utils import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def signup(payload: UserCreationSchema = Body()) -> UserSchema:
    payload.password = hash_password(payload.password)
    return await create_user(user_data=payload, session=...)
