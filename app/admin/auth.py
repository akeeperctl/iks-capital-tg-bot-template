import logging
import secrets
import string
from typing import Final

import bcrypt
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
                "An unexpected error occurred during login. Please contact administrator",
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


## Akeeper 16.10.2025
def generate_password(length: int = 12):
    """
    Генерация пароля с использованием модуля secrets

    Args:
        length: Длина пароля (по умолчанию 12 символов)

    Returns:
        str: пароль
    """

    # Символы для генерации пароля
    special = "!@#$%^&*"
    alphabet = string.ascii_letters + string.digits + special

    # Генерируем пароль используя cryptographically secure random
    password = "".join(secrets.choice(alphabet) for _ in range(length))

    # Убеждаемся что пароль содержит хотя бы одну цифру, букву и спецсимвол
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in special for c in password)

    # Если пароль не соответствует требованиям, генерируем заново
    if not all([has_lower, has_upper, has_digit, has_special]):
        return generate_password(length)

    return password


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8",
    )


## ~Akeeper
