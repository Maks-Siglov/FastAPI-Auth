from src.db.models import User
from src.db.session import s


async def increase_balance(user: User, amount: int) -> None:
    try:
        user.balance += amount
        await s.user_db.commit()
    except Exception as e:
        await s.user_db.rollback()
        raise e


async def decrease_balance(user: User, amount: int) -> None:
    try:
        user.balance -= amount
        await s.user_db.commit()
    except Exception as e:
        await s.user_db.rollback()
        raise e
