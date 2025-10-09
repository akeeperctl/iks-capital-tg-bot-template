from .base import EnvSettings


class CommonConfig(EnvSettings, env_prefix="COMMON_"):
    log_level: str = "INFO"
