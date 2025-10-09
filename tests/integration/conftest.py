from typing import Any, Callable, Coroutine

import pytest_asyncio

from app.models.config import AppConfig
from app.models.sql import User
from app.services.postgres import Repository
from app.services.user import UserService


@pytest_asyncio.fixture
async def user_service(
    repository: Repository,
    app_config: AppConfig,
) -> UserService:
    """Создаёт экземпляр UserService."""
    return UserService(repository=repository, config=app_config)


@pytest_asyncio.fixture
async def create_test_user(repository: Repository) -> Callable[[], Coroutine[Any, Any, User]]:
    """Создаёт тестового пользователя с настраиваемыми параметрами."""

    async def _impl(
        telegram_id: int | None = None,
        name: str | None = None,
        username: str | None = None,
        language: str = "ru",
        language_code: str | None = None,
        bot_blocked: bool = False,
    ) -> User:
        """
        Создаёт пользователя с заданными параметрами.
        """

        if telegram_id is None:
            telegram_id = 100000000 + len(repository.session.identity_map)

        if name is None:
            name = f"Test User {telegram_id}"

        user = User(
            telegram_id=telegram_id,
            name=name,
            username=username,
            language=language,
            language_code=language_code,
            bot_blocked=bot_blocked,
        )

        repository.session.add(user)
        await repository.session.flush()
        return user

    return _impl


@pytest_asyncio.fixture
async def test_user(repository: Repository, create_test_user) -> User:
    """Создаёт базового тестового пользователя."""
    return await create_test_user(
        telegram_id=123456789,
        name="TestUser",
        username="test_user",
        language="ru",
        language_code="ru",
    )
