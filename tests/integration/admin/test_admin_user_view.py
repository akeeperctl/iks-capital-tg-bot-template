from unittest.mock import Mock

import pytest
import pytest_asyncio
from starlette.requests import Request
from starlette_admin.exceptions import ActionFailed, FormValidationError

from app.admin.views.admin_user import AdminUserView
from app.admin.views.base import ValidationTypesEnum
from app.models.sql import AdminUser
from app.services.postgres import Repository
from app.services.user import AdminUserService


@pytest_asyncio.fixture
async def admin_user_service(repository: Repository, app_config) -> AdminUserService:
    return AdminUserService(repository=repository, config=app_config)


@pytest_asyncio.fixture
async def admin_view() -> AdminUserView:
    return AdminUserView(model=AdminUser)


@pytest_asyncio.fixture
async def mock_request(admin_user_service: AdminUserService) -> Mock:
    request = Mock(spec=Request)
    request.state = Mock()
    request.state.admin_user_service = admin_user_service
    request.session = {}
    request.url_for = Mock(return_value="/admin/list")
    return request


@pytest_asyncio.fixture
async def super_admin_request(mock_request: Mock) -> Mock:
    mock_request.state.user = Mock(is_super_admin=True)
    return mock_request


@pytest_asyncio.fixture
async def super_admin_create_request(mock_request: Mock) -> Mock:
    mock_request.state.user = Mock(is_super_admin=True)
    mock_request.session.update(validation_type=ValidationTypesEnum.CREATE.value)
    return mock_request


@pytest_asyncio.fixture
async def super_admin_edit_request(mock_request: Mock) -> Mock:
    mock_request.state.user = Mock(is_super_admin=True)
    mock_request.session.update(validation_type=ValidationTypesEnum.EDIT.value)
    return mock_request


@pytest_asyncio.fixture
async def regular_admin_request(mock_request: Mock) -> Mock:
    mock_request.state.user = Mock(is_super_admin=False)
    return mock_request


@pytest_asyncio.fixture
async def create_admin_user(repository: Repository):

    async def _impl(
            name: str = "TestAdmin",
            username: str = "test_admin",
            password_hash: str = "hashed_password",
            is_super_admin: bool = False,
            is_blocked: bool = False,
    ) -> AdminUser:
        admin = AdminUser(
            name=name,
            username=username,
            password=password_hash,
            is_super_admin=is_super_admin,
            is_blocked=is_blocked,
        )
        repository.session.add(admin)
        await repository.session.flush()
        await repository.session.refresh(admin)
        return admin

    return _impl


@pytest.mark.asyncio
class TestAdminUserCreate:

    async def test_create_admin_user_success(
            self,
            admin_view: AdminUserView,
            super_admin_request: Mock,
            repository: Repository,
    ):

        data = {
            "name": "New Admin",
            "username": "new_admin",
            "is_super_admin": False,
        }

        super_admin_request.session.update(validation_type=ValidationTypesEnum.CREATE.value)
        result = await admin_view.create(super_admin_request, data)

        assert result is not None
        assert result.name == "New Admin"
        assert result.username == "new_admin"
        assert result.is_super_admin is False
        assert "show_info_modal" in super_admin_request.session
        assert super_admin_request.session["show_info_modal"] is True

    async def test_create_generates_password(
            self,
            admin_view: AdminUserView,
            super_admin_request: Mock,
    ):

        data = {
            "name": "Admin With Password",
            "username": "admin_pwd",
            "is_super_admin": True,
        }

        result = await admin_view.create(super_admin_request, data)

        assert result is not None
        modal_data = super_admin_request.session.get("info_modal_data")
        assert modal_data is not None
        assert "password" in modal_data or "data" in modal_data


@pytest.mark.asyncio
class TestAdminUserEdit:

    async def test_edit_admin_name(
            self,
            admin_view: AdminUserView,
            super_admin_edit_request: Mock,
            create_admin_user,
    ):

        admin = await create_admin_user(name="Old Name")

        data = admin.dto().model_dump()
        data.update(
            name="Updated Name",
            updated_at=admin.updated_at,
            created_at=admin.created_at,
        )

        admin = await admin_view.edit(super_admin_edit_request, admin.user_id, data)

        # Проверка, что имя изменилось
        assert admin.name == "Updated Name"

    async def test_edit_cannot_change_username(
            self,
            admin_view: AdminUserView,
            super_admin_request: Mock,
            create_admin_user,
    ):

        admin = await create_admin_user(username="original_username")

        data = {"username": "new_username", "name": "Name"}

        # username должен быть исключён из редактирования
        assert "username" in admin_view.exclude_fields_from_edit


@pytest.mark.asyncio
class TestAdminUserValidation:

    async def test_validate_name_min_length(
            self,
            admin_view: AdminUserView,
            super_admin_create_request: Mock,
    ):

        data = {"name": "ab", "username": "valid_user"}  # name < 5 символов

        with pytest.raises(FormValidationError) as exc_info:
            await admin_view.validate(super_admin_create_request, data)

        errors = exc_info.value.errors
        assert "name" in errors

    async def test_validate_username_min_length(
            self,
            admin_view: AdminUserView,
            super_admin_create_request: Mock,
    ):

        data = {"name": "Valid Name", "username": "abc"}  # username < 5

        with pytest.raises(FormValidationError) as exc_info:
            await admin_view.validate(super_admin_create_request, data)

        errors = exc_info.value.errors
        assert "username" in errors

    async def test_validate_success_with_valid_data(
            self,
            admin_view: AdminUserView,
            super_admin_create_request: Mock,
    ):

        data = {
            "name": "Valid Admin Name",
            "username": "valid_username",
            "is_super_admin": False,
        }

        # Не должно быть исключений
        await admin_view.validate(super_admin_create_request, data)


@pytest.mark.asyncio
class TestAdminUserSecurity:

    async def test_only_super_admin_can_create(
            self,
            admin_view: AdminUserView,
            regular_admin_request: Mock,
    ):

        assert admin_view.can_create(regular_admin_request) is False

    async def test_super_admin_can_create(
            self,
            admin_view: AdminUserView,
            super_admin_request: Mock,
    ):

        assert admin_view.can_create(super_admin_request) is True

    async def test_only_super_admin_can_delete(
            self,
            admin_view: AdminUserView,
            regular_admin_request: Mock,
    ):

        assert admin_view.can_delete(regular_admin_request) is False

    async def test_super_admin_can_delete(
            self,
            admin_view: AdminUserView,
            super_admin_request: Mock,
    ):

        assert admin_view.can_delete(super_admin_request) is True


@pytest.mark.asyncio
class TestAdminUserResetPassword:

    async def test_reset_password_success(
            self,
            admin_view: AdminUserView,
            super_admin_request: Mock,
            create_admin_user,
    ):

        admin = await create_admin_user(username="admin_to_reset")

        await admin_view.reset_password_action(
            super_admin_request,
            admin.user_id,
        )

        assert "show_info_modal" in super_admin_request.session
        assert "info_modal_data" in super_admin_request.session
        assert super_admin_request.session["show_info_modal"] is True
        assert len(super_admin_request.session["info_modal_data"].keys()) > 0

    async def test_reset_password_nonexistent_admin(
            self,
            admin_view: AdminUserView,
            super_admin_request: Mock,
    ):

        with pytest.raises(ActionFailed):
            await admin_view.reset_password_action(super_admin_request, 99999)


@pytest.mark.asyncio
class TestAdminUserFields:

    async def test_exclude_fields_from_create(self, admin_view: AdminUserView):

        excluded = admin_view.exclude_fields_from_create
        assert "user_id" in excluded
        assert "created_at" in excluded

    async def test_exclude_fields_from_edit(self, admin_view: AdminUserView):

        excluded = admin_view.exclude_fields_from_edit
        assert "username" in excluded
        assert "user_id" in excluded
