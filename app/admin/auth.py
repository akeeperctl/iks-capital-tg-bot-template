import logging
from typing import Final

from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed

logger: Final[logging.Logger] = logging.getLogger(name=__name__)


class CustomAuthProvider(AuthProvider):
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if not username or len(username) < 5:
            raise FormValidationError({"username": "Username must be at least 5 characters"})

        if not password or len(password) < 8:
            raise FormValidationError({"password": "Password must be at least 8 characters"})

        try:
            user = await request.state.admin_user_service.get_by_username(username=username)
        except Exception:
            logger.exception("Error while logging in")
            raise LoginFailed(
                "An unexpected error occurred during login. Please contact administrator"
            )

        if not user:
            raise LoginFailed("Invalid username")

        if not user.check_password(password):
            raise LoginFailed("Invalid password")

        if user.is_blocked:
            raise LoginFailed("Your account is blocked")

        request.session.update(
            {
                "username": user.username,
                "user_id": user.user_id,
            },
        )
        logger.info(f"User user_id: {user.user_id}, username: {user.username} logged in")
        return response

    async def is_authenticated(self, request: Request) -> bool:
        try:
            username = request.session.get("username")
            if not username:
                return False

            user = await request.state.admin_user_service.get_by_username(username=username)
            if not user:
                return False

            if user.is_blocked:
                return False

            request.state.user = user
            return True
        except Exception:
            return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        return AdminConfig(app_title="Admin panel", logo_url=None)

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user
        return AdminUser(username=user.username, photo_url=None)

    async def logout(self, request: Request, response: Response) -> Response:
        user = request.state.user
        request.session.clear()
        logger.info(f"User user_id: {user.user_id}, username: {user.username} logout.")
        return response
