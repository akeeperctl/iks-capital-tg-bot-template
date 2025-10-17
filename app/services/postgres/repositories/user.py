from typing import Any, Optional, cast

from sqlalchemy import select
from sqlalchemy.sql.functions import count

from app.models.sql import AdminUser, User
from .base import BaseRepository


class AdminUsersRepository(BaseRepository):
    async def get_by_username(self, username: str) -> Optional[AdminUser]:
        stmt = select(AdminUser).where(AdminUser.username == username)
        return await self.session.scalar(stmt)

    ## Akeeper 16.10.2025
    async def get_one_or_none(self, **filter_by):
        stmt = select(AdminUser).filter_by(**filter_by)
        return await self.session.scalar(stmt)

    ## ~Akeeper

    async def update(self, username: str, **data: Any) -> Optional[AdminUser]:
        return await self._update(
            model=AdminUser,
            conditions=[AdminUser.username == username],
            load_result=True,
            **data,
        )


# noinspection PyTypeChecker
class UsersRepository(BaseRepository):
    async def get(self, user_id: int) -> Optional[User]:
        return await self._get(User, User.user_id == user_id)

    async def get_many(self, ids: list[int]) -> list[User | None]:
        return await self._get_many(User, User.user_id.in_(ids))

    async def get_by_tg_id(self, telegram_id: int) -> Optional[User]:
        return await self._get(User, User.telegram_id == telegram_id)

    async def get_all(self) -> list[User]:
        return await self._get_many(User)

    async def update(self, user_id: int, **data: Any) -> Optional[User]:
        return await self._update(
            model=User,
            conditions=[User.user_id == user_id],
            load_result=True,
            **data,
        )

    async def count(self) -> int:
        return cast(int, await self.session.scalar(select(count(User.user_id))))

    async def delete(self, user_id: int) -> None:
        return await self._delete(User, User.user_id == user_id)
