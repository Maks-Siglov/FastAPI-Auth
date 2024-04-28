from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas.user import UserCreationSchema, UserSchema
from models import User


async def create_user(
    session: AsyncSession, user_data: UserCreationSchema
) -> UserSchema:
    db_user = User(**user_data.dict())
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return UserSchema(**db_user.__dict__)


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    query = select(User).filter(User.email == email)
    return await session.scalar(query)
