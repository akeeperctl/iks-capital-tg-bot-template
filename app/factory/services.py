from __future__ import annotations

from typing import Any, TypedDict

from app.models.config import AppConfig
from app.services.postgres.repositories.base import BaseRepository
from app.services.user import AdminUserService, UserService


class Services(TypedDict):
    user_service: UserService
    admin_user_service: AdminUserService


def create_services(
    repository: BaseRepository,
    config: AppConfig,
) -> Services:
    service_kwargs: dict[str, Any] = {
        "repository": repository,
        "config": config,
    }

    user_service: UserService = UserService(**service_kwargs)
    admin_user_service: AdminUserService = AdminUserService(**service_kwargs)

    return Services(
        user_service=user_service,
        admin_user_service=admin_user_service,
    )
