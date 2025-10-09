from __future__ import annotations

import logging
from typing import Final

from fastapi import FastAPI

from app.endpoints.telegram import TelegramRequestHandler

logger: Final[logging.Logger] = logging.getLogger(name=__name__)


async def close_sessions() -> None:
    """Закрывает соединения при завершении работы"""
    logger.info("Closed all existing connections")


async def emit_aiogram_shutdown(app: FastAPI) -> None:
    handler: TelegramRequestHandler = app.state.tg_webhook_handler
    await handler.shutdown()
    logger.info("Aiogram shutdown completed")
    app.state.shutdown_completed = True
