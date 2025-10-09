import pytest

from app.models.sql import User
from app.services.postgres import Repository
from app.services.user import UserService


class TestUserService:
    """Тесты для работы с пользователем."""

    @pytest.mark.asyncio
    async def test_get_user_by_tg_id(self, test_user: User, user_service: UserService):
        """Тест получения пользователя по telegram_id."""
        user = await user_service.get_by_tg_id(test_user.telegram_id)

        assert user is not None
        assert user.user_id == test_user.user_id
        assert user.telegram_id == 123456789
        assert user.name == "TestUser"
        assert user.username == "test_user"
        assert user.language == "ru"
        assert user.language_code == "ru"

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, test_user: User, user_service: UserService):
        """Тест получения пользователя по user_id."""
        user = await user_service.get(test_user.user_id)

        assert user is not None
        assert user.user_id == test_user.user_id
        assert user.telegram_id == test_user.telegram_id
        assert user.name == "TestUser"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "field, value",
        [
            ("language", "en"),
            ("name", "New test name"),
            ("bot_blocked", True),
        ],
    )
    async def test_update_user(
        self,
        repository: Repository,
        test_user: User,
        user_service: UserService,
        field: str,
        value: str | bool,
        caplog,
    ):
        """Тест обновления данных пользователя."""
        user = await user_service.get_by_tg_id(test_user.telegram_id)
        assert user is not None

        data = {field: value}
        updated_user = await user_service.update(user, **data)

        assert updated_user is not None
        assert getattr(updated_user, field) == value
        assert f"User: {test_user.user_id} was updated" in caplog.messages

    @pytest.mark.asyncio
    async def test_get_all_users(self, test_user: User, user_service: UserService):
        """Тест получения всех пользователей."""
        users = await user_service.get_all()

        assert users is not None
        assert len(users) >= 1
        assert any(u.user_id == test_user.user_id for u in users)

    @pytest.mark.asyncio
    async def test_count_users(self, test_user: User, user_service: UserService):
        """Тест подсчёта пользователей."""
        count = await user_service.count()

        assert count >= 1

    @pytest.mark.asyncio
    async def test_delete_user(
        self, repository: Repository, create_test_user, user_service: UserService
    ):
        """Тест удаления пользователя."""
        # Создаём отдельного пользователя для удаления
        user_to_delete = await create_test_user(
            telegram_id=999999999,
            name="User to delete",
        )

        # Проверяем, что пользователь существует
        user = await user_service.get(user_to_delete.user_id)
        assert user is not None

        # Удаляем пользователя
        await user_service.delete(user_to_delete.user_id)
        await repository.session.commit()

        # Проверяем, что пользователь удалён
        deleted_user = await user_service.get(user_to_delete.user_id)
        assert deleted_user is None
