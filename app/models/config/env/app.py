from pydantic import BaseModel

from .admin import AdminConfig
from .common import CommonConfig
from .middleware import MiddlewareConfig
from .postgres import PostgresConfig
from .server import ServerConfig
from .sql_alchemy import SQLAlchemyConfig
from .telegram import TelegramConfig


class AppConfig(BaseModel):
    telegram: TelegramConfig
    postgres: PostgresConfig
    sql_alchemy: SQLAlchemyConfig
    server: ServerConfig
    common: CommonConfig
    admin: AdminConfig
    middleware: MiddlewareConfig
