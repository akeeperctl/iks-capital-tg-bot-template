import asyncio

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

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
from app.services.postgres import Repository
from app.services.postgres.context import SQLSessionContext
from app.utils.logging import setup_logger


@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    setup_logger()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def postgres_config() -> PostgresConfig:
    return PostgresConfig()


@pytest.fixture
def telegram_config() -> TelegramConfig:
    return TelegramConfig()


@pytest.fixture
def sqlalchemy_config() -> SQLAlchemyConfig:
    return SQLAlchemyConfig()


@pytest.fixture
def server_config() -> ServerConfig:
    return ServerConfig()


@pytest.fixture
def common_config() -> CommonConfig:
    return CommonConfig()


@pytest.fixture
def admin_config() -> AdminConfig:
    return AdminConfig()


@pytest.fixture
def middleware_config() -> MiddlewareConfig:
    return MiddlewareConfig()


@pytest.fixture
def app_config(
    telegram_config: TelegramConfig,
    postgres_config: PostgresConfig,
    sqlalchemy_config: SQLAlchemyConfig,
    server_config: ServerConfig,
    common_config: CommonConfig,
    admin_config: AdminConfig,
    middleware_config: MiddlewareConfig,
) -> AppConfig:
    return AppConfig(
        telegram=telegram_config,
        postgres=postgres_config,
        sql_alchemy=sqlalchemy_config,
        server=server_config,
        common=common_config,
        admin=admin_config,
        middleware=middleware_config,
    )


@pytest_asyncio.fixture
async def async_engine(postgres_config: PostgresConfig) -> AsyncEngine:  # type: ignore
    """Создаёт асинхронный движок SQLAlchemy."""
    database_url = postgres_config.build_url()
    engine = create_async_engine(database_url, echo=False)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def repository(async_engine) -> Repository:  # type: ignore
    session_pull = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with SQLSessionContext(session_pool=session_pull) as repository:
        yield repository

        # Очищаем данные после теста
        await repository.session.rollback()
