from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator

from aiogram import Bot, Dispatcher, loggers
from aiogram.methods import SetWebhook
from fastapi import FastAPI

from app.endpoints.telegram import TelegramRequestHandler

if TYPE_CHECKING:
    from app.models.config import AppConfig


async def webhook_startup(
    dispatcher: Dispatcher,
    bot: Bot,
    config: AppConfig,
) -> None:
    url: str = config.server.build_url(path=config.telegram.webhook_path)
    method: SetWebhook = SetWebhook(
        url=url,
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=config.telegram.webhook_secret.get_secret_value(),
        drop_pending_updates=config.telegram.drop_pending_updates,
    )

    if not await bot(method):
        raise RuntimeError(f"Failed to set main bot webhook on url '{url}'")

    loggers.webhook.info("Main bot webhook successfully set on url '%s'", url)


async def webhook_shutdown(
    bot: Bot,
    config: AppConfig,
) -> None:
    if not config.telegram.reset_webhook:
        return
    if await bot.delete_webhook():
        loggers.webhook.info("Dropped main bot webhook.")
    else:
        loggers.webhook.error("Failed to drop main bot webhook.")
    await bot.session.close()


@asynccontextmanager
async def webhook_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    handler: TelegramRequestHandler = app.state.tg_webhook_handler

    await handler.startup()
    yield
    await handler.shutdown()
