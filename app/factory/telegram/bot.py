from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

if TYPE_CHECKING:
    from app.models.config import AppConfig


def create_bot(config: AppConfig) -> Bot:
    return Bot(
        token=config.telegram.bot_token.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )
