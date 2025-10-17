import logging
from typing import Any, get_args

from pydantic import ValidationError
from starlette.requests import Request
from starlette_admin import (
    BooleanField,
    EnumField,
    IntegerField,
    StringField,
)
from starlette_admin.helpers import pydantic_error_to_form_validation_errors

from app.admin.views.base import BaseModelView
from app.models.dto.user import UserEditDto, UserCreateDto
from app.utils.custom_types import AllowedLanguages

logger: logging.Logger = logging.getLogger(__name__)


class UserView(BaseModelView):

    fields = [
        IntegerField(
            name="user_id",
            label="ID",
            # exclude_from_edit=True,
        ),
        IntegerField(
            name="telegram_id",
            label="Telegram ID",
            #             exclude_from_edit=True,
        ),
        StringField(
            name="name",
            label="Name",
        ),
        StringField(
            name="username",
            label="Username",
            # exclude_from_edit=True,
        ),
        BooleanField(
            name="bot_blocked",
            label="Bot blocked",
            # exclude_from_edit=True,
        ),
        EnumField(
            name="language",
            label="Language",
            choices=get_args(AllowedLanguages),
        ),
    ]

    ## Akeeper 17.10.2025
    exclude_fields_from_create = [
        i.name for i in fields if i.name not in UserCreateDto.model_fields
    ]
    exclude_fields_from_edit = [
        i.name for i in fields if i.name not in UserEditDto.model_fields
    ]

    async def validate(self, request: Request, data: dict[str, Any]) -> None:
        dto = self.select_dto_by_validation_type(request, UserCreateDto, UserEditDto)

        try:
            dto.model_validate(data)
        except ValidationError as e:
            # Переводит pydantic ошибки в формат StarletteAdmin (dict field -> error)
            raise pydantic_error_to_form_validation_errors(e)

        return await super().validate(request, data)

    ## ~Akeeper

    def can_create(self, request: Request) -> bool:
        return self.is_super_admin(request)

    def can_delete(self, request: Request) -> bool:
        return self.is_super_admin(request)
