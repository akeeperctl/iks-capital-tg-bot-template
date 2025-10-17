import logging
from typing import Any

from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette_admin import (
    BooleanField,
    IntegerField,
    StringField,
    DateField,
    row_action,
)
from starlette_admin.exceptions import ActionFailed
from starlette_admin.helpers import pydantic_error_to_form_validation_errors

from app.admin.auth import generate_password
from app.admin.views.base import BaseModelView, ValidationTypesEnum
from app.models.dto.user import AdminUserCreateWithPwdDto, AdminUserCreateDto, AdminUserEditDto
from app.services.user import AdminUserService

logger: logging.Logger = logging.getLogger(__name__)


class AdminUserView(BaseModelView):

    row_actions = ["reset_password", "delete", "edit"]

    # Использует кастомные шаблоны для вывода нового модального окна
    list_template = "admin/list.html"
    create_template = "admin/create.html"
    edit_template = "admin/edit.html"

    fields = [
        IntegerField(
            name="user_id",
            label="ID",
        ),
        StringField(
            name="name",
            label="Name",
        ),
        StringField(
            name="username",
            label="Username",
        ),
        BooleanField(
            name="is_blocked",
            label="Is blocked",
        ),
        BooleanField(
            name="is_super_admin",
            label="Is super admin",
        ),
        DateField(
            name="created_at",
            label="Created at",
        ),
    ]

    # Исключает поля, которых нет в схеме
    exclude_fields_from_create = [
        i.name for i in fields if i.name not in AdminUserCreateDto.model_fields
    ]
    exclude_fields_from_edit = [
        i.name for i in fields if i.name not in AdminUserEditDto.model_fields
    ]

    @row_action(
        name="reset_password",
        text="Сбросить пароль",
        confirmation="Вы уверены что хотите сбросить пароль этого администратора?",
        icon_class="fas fa-key",
        submit_btn_text="Да, сбросить",
        submit_btn_class="btn-warning",
        action_btn_class="btn-outline-warning",
        custom_response=True,
    )
    async def reset_password_action(self, request: Request, pk: Any):
        admin_user_service: AdminUserService = request.state.admin_user_service

        try:
            admin_user = await admin_user_service.get_by_id(user_id=int(pk))
            if not admin_user:
                raise ActionFailed(f"Администратор c pk == {pk} не найден")

            new_password = generate_password()

            success = await admin_user_service.update_password(
                username=admin_user.username,
                new_password=new_password,
            )

            if not success:
                raise ActionFailed(f"Ошибка при обновлении пароля")

            # Пишет пароль во временную переменную сессии
            await self.show_info_modal(
                request=request,
                message=f"Новый пароль для администратора {admin_user.username}: ",
                data=new_password,
            )

            return RedirectResponse(request.url_for("admin:list", identity=self.identity))

        except Exception as e:
            raise ActionFailed(f"Ошибка при сбросе пароля: {str(e)}")

    async def validate(self, request: Request, data: dict[str, Any]) -> None:

        # NOTE: если проверяемое поле отсутствует в форме, то исключение
        #   валидации будет "проглочено" и не будет отображено для этого поля.
        #   Соответственно страница просто обновится без каких-либо видимых ошибок,
        #   что вызовет вопрос "Почему оно не обновилось и ошибку не показало".

        dto = self.select_dto_by_validation_type(request, AdminUserCreateDto, AdminUserEditDto)
        try:
            dto.model_validate(data)
        except ValidationError as e:
            # Переводит pydantic ошибки в формат StarletteAdmin (dict field -> error)
            raise pydantic_error_to_form_validation_errors(e)

        return await super().validate(request, data)

    async def create(self, request: Request, data: dict) -> Any:
        request.session.update(validation_type=ValidationTypesEnum.CREATE.value)
        await self.validate(request, data)

        generated_password = generate_password()

        _data = AdminUserCreateWithPwdDto.model_validate(data)
        _data.password = generated_password

        admin_user_service: AdminUserService = request.state.admin_user_service
        admin_user = await admin_user_service.create(_data)

        # Пишет пароль во временную переменную сессии
        await self.show_info_modal(
            request=request,
            message=f"Сырой пароль созданного администратора {admin_user.username}: ",
            data=generated_password,
        )

        # NOTE: обязательно возвращать созданный объект!
        #   Иначе будет 500 при "Save and continue editing"
        #   потому что не смог найти созданный объект.
        return admin_user

    def can_create(self, request: Request) -> bool:
        return self.is_super_admin(request)

    def can_delete(self, request: Request) -> bool:
        return self.is_super_admin(request)
