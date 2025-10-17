import enum
from abc import ABC
from typing import Optional, Any, Dict

from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView

from app.models.base import PydanticModel


class ValidationTypesEnum(str, enum.Enum):
    EDIT = "edit"
    CREATE = "create"


## Akeeper 16.10.2025
class BaseModelView(ModelView, ABC):

    @staticmethod
    async def show_info_modal(request: Request, message: str, data: Optional[str] = None):
        request.session["show_info_modal"] = True
        request.session["info_modal_data"] = {"message": message, "data": data}

    @staticmethod
    def is_super_admin(request: Request) -> bool | Any:
        user = getattr(request.state, "user", None)
        if not user:
            return False

        return getattr(user, "is_super_admin", False)

    @classmethod
    def select_dto_by_validation_type(
            cls,
            request: Request,
            create_dto: type[PydanticModel],
            edit_dto: type[PydanticModel],
    ) -> type[PydanticModel]:
        """
        Возвращает из запроса PydanticModel, который используется при валидации
        Args:
            edit_dto ():
            create_dto ():
            request (Request): HTTP запрос
        Returns:
            type[PydanticModel]: PydanticModel, через который будет происходить валидация
        """

        dto: Optional[type[PydanticModel]] = None
        validation_type = request.session.get("validation_type")

        if validation_type == ValidationTypesEnum.CREATE.value:
            dto = create_dto
        elif validation_type == ValidationTypesEnum.EDIT.value:
            dto = edit_dto

        return dto

    # Записывает тип валидации, чтобы после определить Pydantic Model, через которую будет валидация
    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        request.session.update(validation_type=ValidationTypesEnum.CREATE.value)
        return await super().create(request, data)

    async def edit(self, request: Request, pk: Any, data: Dict[str, Any]) -> Any:
        request.session.update(validation_type=ValidationTypesEnum.EDIT.value)
        return await super().edit(request, pk, data)

## ~Akeeper
