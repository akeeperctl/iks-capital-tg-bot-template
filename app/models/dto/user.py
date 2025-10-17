from typing import Optional

import bcrypt
from pydantic import Field

from app.models.base import ActiveRecordModel
from app.utils.custom_types import EntityId, Str8, Str5, Str2


class AdminUserDto(ActiveRecordModel):
    user_id: EntityId
    name: Str5
    username: Str5
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
    name: Str5
    username: Str5
    is_super_admin: bool = False


class AdminUserCreateWithPwdDto(AdminUserCreateDto):
    password: Optional[Str8] = None


class UserDto(ActiveRecordModel):
    user_id: EntityId
    telegram_id: EntityId
    name: Str5
    language: str
    username: Optional[Str5] = None
    language_code: Optional[str] = None
    bot_blocked: bool = False
