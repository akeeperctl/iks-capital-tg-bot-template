from typing import Optional

import bcrypt
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, validates
from starlette.requests import Request

from app.models.dto.user import AdminUserDto, UserDto
from app.utils.custom_types import Int64

from .base import Base, auto_int_pk
from .mixins import TimestampMixin

SCHEMA = "users"


class AdminUser(Base, TimestampMixin):
    """Модель администратора"""

    __tablename__ = "admin"
    __table_args__ = {"schema": SCHEMA}

    user_id: Mapped[auto_int_pk]
    name: Mapped[str | None] = mapped_column()
    username: Mapped[str] = mapped_column()
    password: Mapped[str]
    is_blocked: Mapped[bool] = mapped_column(default=False, server_default="false")

    ## Akeeper 16.10.2025
    is_super_admin: Mapped[bool] = mapped_column(default=False, server_default="false")
    ## ~Akeeper

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(user_id={self.user_id})"

    def __repr__(self) -> str:
        return str(self)

    async def __admin_repr__(self, request: Request) -> str:
        return f"{self.name}"

    def dto(self) -> AdminUserDto:
        return AdminUserDto.model_validate(self)

    @validates("username")
    def validate_username(self, key: str, username: str) -> str:
        """
        Валидация username - минимум 5 символов.
        """
        if len(username) < 5:
            raise ValueError("Username must be at least 5 characters long")
        return username

    @validates("password")
    def validate_password(self, key: str, password: str) -> str:
        """
        Валидация и хеширование пароля перед сохранением в базу данных.
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        return hashed_password


class User(Base, TimestampMixin):
    """Модель пользователя бота"""

    __tablename__ = "user"
    __table_args__ = {"schema": SCHEMA}

    user_id: Mapped[auto_int_pk]
    telegram_id: Mapped[Int64] = mapped_column(unique=True)

    name: Mapped[str] = mapped_column()
    username: Mapped[str | None] = mapped_column()
    language: Mapped[str] = mapped_column(String(length=2))
    language_code: Mapped[Optional[str]] = mapped_column()
    bot_blocked: Mapped[bool] = mapped_column(default=False)

    def dto(self) -> UserDto:
        return UserDto.model_validate(self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(user_id={self.user_id}, name={self.name})"

    def __repr__(self) -> str:
        return str(self)
