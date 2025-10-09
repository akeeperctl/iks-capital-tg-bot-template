from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from .user import AdminUsersRepository, UsersRepository


class Repository(BaseRepository):
    users: UsersRepository
    admin_users: AdminUsersRepository

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session)
        self.users = UsersRepository(session=session)
        self.admin_users = AdminUsersRepository(session=session)
