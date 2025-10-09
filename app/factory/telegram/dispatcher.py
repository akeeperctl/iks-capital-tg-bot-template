from __future__ import annotations

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.factory.session_pool import create_session_pool
from app.models.config import AppConfig
from app.telegram.handlers import main
from app.telegram.middlewares import DBSessionMiddleware, UserMiddleware


def create_dispatcher(bot: Bot, config: AppConfig) -> Dispatcher:
    """
    Создает и настраивает Dispatcher с установленными middleware и роутерами

    :return: Настроенный ``Dispatcher``
    """
    session_pool: async_sessionmaker[AsyncSession] = create_session_pool(config=config)

    # noinspection PyArgumentList
    dispatcher: Dispatcher = Dispatcher(
        name="main_dispatcher",
        config=config,
        session_pool=session_pool,
    )

    dispatcher.workflow_data["session_pool"] = session_pool
    dispatcher.include_routers(main.router)
    dispatcher.update.outer_middleware(DBSessionMiddleware())
    dispatcher.update.outer_middleware(UserMiddleware())

    return dispatcher
