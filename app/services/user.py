from typing import Any, Optional

from aiogram.types import User as AiogramUser

from app.models.dto import AdminUserDto, UserDto
from app.models.sql import User, AdminUser
from .base import BaseService
from ..admin.auth import hash_password
from ..models.dto.user import AdminUserCreateWithPwdDto


class AdminUserService(BaseService):
    ## Akeeper 16.10.2025
    async def create(self, data: AdminUserCreateWithPwdDto) -> AdminUserDto:
        _data = data
        _data.password = hash_password(data.password)

        db_admin_user: AdminUser = AdminUser(
            **_data.model_dump(),
        )

        self.session.add(db_admin_user)
        await self.session.flush()
        return db_admin_user.dto()

    async def get_by_id(self, user_id: int) -> AdminUserDto | None:
        obj = await self.repository.admin_users.get_one_or_none(user_id=user_id)
        if obj is None:
            return None
        return obj.dto()

    ## ~Akeeper

    async def get_by_username(self, username: str) -> AdminUserDto | None:
        obj = await self.repository.admin_users.get_by_username(username=username)
        if obj is None:
            return None
        return obj.dto()

    async def update_password(self, username: str, new_password: str) -> bool:
        """Обновляет пароль админа по username."""
        try:
            hashed_password = hash_password(new_password)
            updated_admin = await self.repository.admin_users.update(
                username=username,
                password=hashed_password,
            )
            if updated_admin:
                self.logger.info(f"Password updated successfully for admin: {username}")
                return True
            return False
        except Exception as e:
            self.logger.exception(f"Failed to update password for admin {username}: {e}")
            return False


class UserService(BaseService):
    async def create(
        self,
        aiogram_user: AiogramUser,
        language: str = "en",
    ) -> UserDto:
        db_user: User = User(
            telegram_id=aiogram_user.id,
            name=aiogram_user.full_name,
            username=aiogram_user.username,
            language=language,
            language_code=aiogram_user.language_code,
        )

        self.session.add(db_user)
        await self.session.flush()
        return db_user.dto()

    async def get(self, user_id: int) -> Optional[UserDto]:
        user = await self.repository.users.get(user_id=user_id)
        if user is None:
            return None
        return user.dto()

    async def get_by_tg_id(self, telegram_id: int) -> Optional[UserDto]:
        user = await self.repository.users.get_by_tg_id(telegram_id=telegram_id)
        if user is None:
            return None
        return user.dto()

    async def get_all(self) -> list[UserDto] | None:
        """Получить всех пользователей."""
        users = await self.repository.users.get_all()
        if not users:
            return None
        return [user.dto() for user in users]

    async def count(self) -> int:
        return await self.repository.users.count()

    async def update(self, user: UserDto, **data: Any) -> Optional[UserDto]:
        for key, value in data.items():
            setattr(user, key, value)
        user_db = await self.repository.users.update(user_id=user.user_id, **user.model_state)
        if user_db is None:
            self.logger.error(f"User: {user.user_id} not found for updated!")
            return None
        self.logger.info(f"User: {user.user_id} was updated")
        return user_db.dto()

    async def delete(self, user_id: int) -> None:
        return await self.repository.users.delete(user_id=user_id)
