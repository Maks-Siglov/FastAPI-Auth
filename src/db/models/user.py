from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()

    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)

    role: Mapped[str] = mapped_column(default="user")
    balance: Mapped[int] = mapped_column(default=0)

    is_active: Mapped[bool] = mapped_column(default=True)
    is_blocked: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
    )

    def __str__(self) -> str:
        return self.email
