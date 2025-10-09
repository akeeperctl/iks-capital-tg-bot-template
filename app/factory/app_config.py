from __future__ import annotations

from app.models.config.env import (
    AdminConfig,
    AppConfig,
    CommonConfig,
    MiddlewareConfig,
    PostgresConfig,
    ServerConfig,
    SQLAlchemyConfig,
    TelegramConfig,
)


# noinspection PyArgumentList
def create_app_config() -> AppConfig:
    return AppConfig(
        telegram=TelegramConfig(),
        postgres=PostgresConfig(),
        sql_alchemy=SQLAlchemyConfig(),
        server=ServerConfig(),
        common=CommonConfig(),
        admin=AdminConfig(),
        middleware=MiddlewareConfig(),
    )
