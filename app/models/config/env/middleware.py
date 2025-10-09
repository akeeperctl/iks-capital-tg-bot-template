from pydantic import SecretStr

from app.utils.custom_types import StringList

from .base import EnvSettings


class MiddlewareConfig(EnvSettings, env_prefix="MIDDLEWARE_"):
    # CORS settings
    cors_origins: StringList
    cors_allow_methods: StringList
    cors_allow_headers: StringList
    cors_allow_credentials: bool = True

    # Session settings
    session_secret_key: SecretStr
    session_max_age: int = 3 * 24 * 60 * 60  # 3 days in second
    session_https_only: bool = True
    session_cookie_name: str = "session"
