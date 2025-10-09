import logging
from types import TracebackType
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .repositories import Repository

logger = logging.getLogger(__name__)


class SQLSessionContext:
    _session_pool: async_sessionmaker[AsyncSession]
    _session: Optional[AsyncSession]

    __slots__ = ("_session_pool", "_session")

    def __init__(self, session_pool: async_sessionmaker[AsyncSession]) -> None:
        self._session_pool = session_pool
        self._session = None

    async def __aenter__(self) -> Repository:
        self._session = self._session_pool()
        await self._session.__aenter__()
        logger.debug(f"Async session: {self._session.sync_session.hash_key} initialized!")
        return Repository(session=self._session)

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self._session is None:
            return

        try:
            if exc_type is not None:
                logger.exception(
                    f"Async session: {self._session.sync_session.hash_key} rollback due to exception!"
                )
                await self._session.rollback()
            else:
                await self._session.commit()
        except Exception as e:
            logger.exception(f"Error during session finalization: {e}")
            await self._session.rollback()
        finally:
            logger.debug(f"Async session: {self._session.sync_session.hash_key} closed!")
            await self._session.close()
            self._session = None
