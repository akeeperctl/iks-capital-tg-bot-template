from typing import Optional

import bcrypt
from pydantic import Field

from app.models.base import ActiveRecordModel, PydanticModel
from app.utils.custom_types import Str8, Str5


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


## Akeeper 17.10.2025
class AdminUserCreateDto(PydanticModel):
    name: Str5
    username: Str5
    is_blocked: bool = False
    is_super_admin: bool = False


class AdminUserCreateWithPwdDto(AdminUserCreateDto):
    password: Optional[Str8] = None


class AdminUserEditDto(PydanticModel):
    name: Str5
    is_blocked: bool
    is_super_admin: bool


## ~Akeeper

class UserDto(ActiveRecordModel):
    user_id: int
    telegram_id: int
    name: str
    language: str
    username: Optional[str] = None
    language_code: Optional[str] = None
    bot_blocked: bool = False
