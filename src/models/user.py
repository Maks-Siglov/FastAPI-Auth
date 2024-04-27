from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    __abstract__ = True

    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )

    def __str__(self) -> str:
        return self.email
