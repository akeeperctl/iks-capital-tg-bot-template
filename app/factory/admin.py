from http.client import HTTPException
from typing import Optional, Sequence

from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette_admin.auth import BaseAuthProvider
from starlette_admin.contrib.sqla import Admin

from app.admin.auth import CustomAuthProvider
from app.admin.middlewares import DBSessionMiddleware
from app.admin.views import UserView, AdminUserView
from app.const import TEMPLATES_DIR, STATICS_DIR
from app.models.config import AppConfig
from app.models.sql import User, AdminUser


class CustomAdmin(Admin):
    def __init__(
            self,
            config: AppConfig,
            title: str = "Admin",
            base_url: str = "/admin",
            route_name: str = "admin",
            logo_url: Optional[str] = None,
            login_logo_url: Optional[str] = None,
            auth_provider: Optional[BaseAuthProvider] = None,
            middlewares: Optional[Sequence[Middleware]] = None,
            session_pool=None,
    ) -> None:
        super(Admin, self).__init__(
            title=title,
            base_url=base_url,
            route_name=route_name,
            logo_url=logo_url,
            login_logo_url=login_logo_url,
            auth_provider=auth_provider,
            middlewares=middlewares,
            statics_dir=str(STATICS_DIR),
            templates_dir=str(TEMPLATES_DIR),
        )
        self.config = config
        self.middlewares = [] if self.middlewares is None else list(self.middlewares)
        self.middlewares.insert(
            0,
            Middleware(DBSessionMiddleware, session_pool=session_pool),
        )

    def mount_to(
            self,
            app: Starlette,
            redirect_slashes: bool = True,
    ) -> None:
        admin_app = Starlette(
            routes=self.routes,
            middleware=self.middlewares,
            exception_handlers={HTTPException: self._render_error},
        )
        admin_app.state.ROUTE_NAME = self.route_name
        admin_app.state.config = self.config
        app.mount(
            self.base_url,
            app=admin_app,
            name=self.route_name,
        )
        admin_app.router.redirect_slashes = redirect_slashes


def setup_admin(app: FastAPI, config: AppConfig) -> FastAPI:
    """Настройка админ-панели"""
    session_pool = app.state.session_pool

    admin = CustomAdmin(
        auth_provider=CustomAuthProvider(allow_paths=["/login"]),
        config=config,
        session_pool=session_pool,
        middlewares=[
            Middleware(
                SessionMiddleware,
                secret_key=config.middleware.session_secret_key.get_secret_value(),
                max_age=config.middleware.session_max_age,
                https_only=config.middleware.session_https_only,
                session_cookie=config.middleware.session_cookie_name,
            ),
        ],
    )

    # Add views
    admin.add_view(UserView(User, icon="fa fa-users"))

    ## Akeeper 16.10.2025
    app.mount("/statics", StaticFiles(directory=str(STATICS_DIR)), name="statics")
    admin.add_view(AdminUserView(AdminUser, icon="fa fa-users"))
    ## ~Akeeper

    admin.mount_to(app)

    return app
