import logging

from starlette.requests import Request
from starlette_admin import (
    BooleanField,
    EnumField,
    IntegerField,
    StringField,
)
from starlette_admin.contrib.sqla import ModelView

logger: logging.Logger = logging.getLogger(__name__)


class UserView(ModelView):
    fields = [
        IntegerField(
            name="user_id",
            label="ID",
            exclude_from_edit=True,
        ),
        IntegerField(
            name="telegram_id",
            label="Telegram ID",
            exclude_from_edit=True,
        ),
        StringField(
            name="name",
            label="Name",
        ),
        StringField(
            name="username",
            label="Username",
            exclude_from_edit=True,
        ),
        BooleanField(
            name="bot_blocked",
            label="Bot blocked",
            exclude_from_edit=True,
        ),
        EnumField(
            name="language",
            label="Language",
            choices=["ru", "en"]
        ),
    ]

    def can_create(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False
