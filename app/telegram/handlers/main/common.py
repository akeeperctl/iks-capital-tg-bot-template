from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

if TYPE_CHECKING:
    from app.models.dto import UserDto

router: Final[Router] = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def handle_start(
    message: Message,
    user: UserDto,
) -> Any:
    await message.answer(
        f"Привет, {user.name}!\n\n"
        f"Твой Telegram ID: {user.telegram_id}\n"
        f"Твой ID в базе данных: {user.user_id}\n"
        f"Язык: {user.language}\n\n"
        f"Ты успешно зарегистрирован в базе данных!"
    )
    logger.info(f"User {user.telegram_id} started the bot")
