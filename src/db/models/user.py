from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, validates

from src.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str | None] = mapped_column(unique=True, nullable=True)
    password: Mapped[str] = mapped_column()

    first_name: Mapped[str | None] = mapped_column(nullable=True)
    last_name: Mapped[str | None] = mapped_column(nullable=True)

    role: Mapped[str] = mapped_column(default="user")
    balance: Mapped[int] = mapped_column(default=0)

    is_active: Mapped[bool] = mapped_column(default=True)
    is_blocked: Mapped[bool] = mapped_column(default=False)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
    )

    @validates("role", "balance")
    def validate_admin_balance(self, key, value):
        if key == "role" and value == "admin" and self.balance:
            raise ValueError("Admin users cannot have a balance.")
        if key == "balance" and self.role == "admin" and value:
            raise ValueError("Admin users cannot have a balance.")
        return value

    def __str__(self) -> str:
        return str(self.email)
