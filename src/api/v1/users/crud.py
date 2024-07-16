from sqlalchemy import select

from src.api.v1.users.models.user import UserCreationSchema, UserSchema
from src.db.models import User
from src.db.session import s


async def create_user(user_data: UserCreationSchema) -> UserSchema:
    db_user = User(**user_data.model_dump())
    s.user_db.add(db_user)
    await s.user_db.commit()
    await s.user_db.refresh(db_user)
    return UserSchema.model_validate(db_user)


async def activate_user(user: User) -> None:
    user.is_active = True
    await s.user_db.commit()
    await s.user_db.refresh(user)


async def deactivate_my_user(user: User) -> None:
    user.is_active = False
    await s.user_db.commit()
    await s.user_db.refresh(user)


async def change_user_password(user: User, new_password: str) -> None:
    user.password = new_password
    await s.user_db.commit()
    await s.user_db.refresh(user)


async def get_user_by_email(email: str) -> User | None:
    query = select(User).filter(User.email == email)
    return await s.user_db.scalar(query)


async def get_user(user_id: int) -> User | None:
    return await s.user_db.get(User, user_id)
