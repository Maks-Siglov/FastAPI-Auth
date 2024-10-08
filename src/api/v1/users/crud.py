from sqlalchemy import select

from src.api.v1.users.models.user import UserCreationSchema
from src.db.models import User
from src.db.session import s


async def create_user(user_data: UserCreationSchema) -> User:
    db_user = User(**user_data.model_dump())
    s.user_db.add(db_user)
    await s.user_db.commit()
    await s.user_db.refresh(db_user)
    return db_user


async def activate_user(user: User) -> None:
    user.is_active = True
    await s.user_db.commit()
    await s.user_db.refresh(user)


async def deactivate_my_user(user: User) -> None:
    user.is_active = False
    await s.user_db.commit()
    await s.user_db.refresh(user)


async def delete_my_user(user: User) -> None:
    user.is_active = False
    user.is_deleted = True
    user.email = None
    user.first_name = None
    user.last_name = None
    await s.user_db.commit()
    await s.user_db.refresh(user)


async def change_user_password(user: User, new_password: str) -> None:
    user.password = new_password
    await s.user_db.commit()
    await s.user_db.refresh(user)


async def get_user_by_email(email: str) -> User | None:
    query = select(User).filter(User.email == email)
    return await s.user_db.scalar(query)


async def get_user_by_id(user_id: int) -> User | None:
    return await s.user_db.get(User, user_id)


async def edit_user(user: User, edited_data: dict[str, str]) -> User:
    for field, value in edited_data.items():
        if hasattr(user, field):
            setattr(user, field, value)

    await s.user_db.commit()
    await s.user_db.refresh(user)
    return user


async def block_my_user(user: User) -> None:
    user.is_blocked = True
    await s.user_db.commit()
    await s.user_db.refresh(user)


async def unblock_my_user(user: User) -> None:
    user.is_blocked = False
    await s.user_db.commit()
    await s.user_db.refresh(user)
