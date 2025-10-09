import abc
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.config import AppConfig
from app.services.postgres import Repository


class BaseService(abc.ABC):
    repository: Repository
    session: AsyncSession
    config: AppConfig

    def __init__(
        self,
        repository: Repository,
        config: AppConfig,
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.repository = repository
        self.session = self.repository.session
        self.config = config
