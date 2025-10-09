from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Optional

from aiogram.types import TelegramObject
from aiogram.types import User as AiogramUser

from app.const import DEFAULT_LOCALE
from app.models.dto import UserDto
from app.services.user import UserService

from .event_typed import EventTypedMiddleware

logger = logging.getLogger(__name__)


class UserMiddleware(EventTypedMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Optional[Any]:
        aiogram_user: Optional[AiogramUser] = data.get("event_from_user")
        if aiogram_user is None or aiogram_user.is_bot:
            return await handler(event, data)

        logger.info(
            "User interaction: telegram_id=%d, username=%s, name=%s",
            aiogram_user.id,
            aiogram_user.username,
            aiogram_user.full_name,
        )

        user_service: UserService = data["user_service"]
        config = user_service.config
        user: Optional[UserDto] = await user_service.get_by_tg_id(telegram_id=aiogram_user.id)

        if user is None:
            # Определяем язык из доступных locales
            available_locales = list(config.telegram.locales)
            language = (
                aiogram_user.language_code
                if aiogram_user.language_code in available_locales
                else DEFAULT_LOCALE
            )

            user = await user_service.create(
                aiogram_user=aiogram_user,
                language=language,
            )
            logger.info(
                "New user in database: %s (%d) %s",
                aiogram_user.full_name,
                aiogram_user.id,
                user.username,
            )

        data["user"] = user
        return await handler(event, data)
