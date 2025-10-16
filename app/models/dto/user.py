from typing import Optional

import bcrypt
from pydantic import Field

from app.models.base import ActiveRecordModel


class AdminUserDto(ActiveRecordModel):
    user_id: int
    name: str
    username: str
    password_hash: str = Field(..., alias="password")
    is_blocked: bool = False

    ## Akeeper 16.10.2025
    is_super_admin: bool = False
    ## ~Akeeper

    def check_password(self, password: str) -> bool:
        """
        Проверка, соответствует ли предоставленный пароль сохраненному хешу.
        """
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))


class AdminUserCreateDto(ActiveRecordModel):
    name: str
    username: str
    is_superuser: bool = False


class UserDto(ActiveRecordModel):
    user_id: int
    telegram_id: int
    name: str
    language: str
    username: Optional[str] = None
    language_code: Optional[str] = None
    bot_blocked: bool = False
