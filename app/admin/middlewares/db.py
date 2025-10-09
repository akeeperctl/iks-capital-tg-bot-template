import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.factory.services import create_services
from app.services.postgres import SQLSessionContext

logger = logging.getLogger(__name__)


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, session_pool: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(app)
        self.session_pool = session_pool

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Исключаем запросы для статики
        path = request.url.path
        if path.startswith("/admin/statics/"):
            return await call_next(request)

        async with SQLSessionContext(self.session_pool) as repository:
            # Сессия нужная для работы встроенных методов по формированию views
            request.state.session = repository.session
            services = create_services(
                repository=repository,
                config=request.app.state.config,
            )
            # Сохраняем сервисы как отдельные атрибуты
            request.state.user_service = services["user_service"]
            request.state.admin_user_service = services["admin_user_service"]

            return await call_next(request)
