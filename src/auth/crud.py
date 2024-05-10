from sqlalchemy import select

from auth.schemas.user import UserCreationSchema, UserSchema
from db.main import s
from models import User


async def create_user(user_data: UserCreationSchema) -> UserSchema:
    db_user = User(**user_data.model_dump())
    s.user_db.add(db_user)
    await s.user_db.commit()
    await s.user_db.refresh(db_user)
    return UserSchema(**db_user.__dict__)


async def get_user_by_email(email: str) -> User | None:
    query = select(User).filter(User.email == email)
    return await s.user_db.scalar(query)
