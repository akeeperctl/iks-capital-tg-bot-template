from aiogram import Bot, Dispatcher
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.admin.middlewares import DBSessionMiddleware
from app.endpoints import healthcheck
from app.models.config import AppConfig


def setup_fastapi(app: FastAPI, dispatcher: Dispatcher, bot: Bot, config: AppConfig) -> FastAPI:
    app.add_middleware(
        DBSessionMiddleware, session_pool=dispatcher.workflow_data.get("session_pool")
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.middleware.session_secret_key.get_secret_value(),
        max_age=config.middleware.session_max_age,
        https_only=config.middleware.session_https_only,
        session_cookie=config.middleware.session_cookie_name,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.middleware.cors_origins,
        allow_credentials=config.middleware.cors_allow_credentials,
        allow_methods=config.middleware.cors_allow_methods,
        allow_headers=config.middleware.cors_allow_headers,
    )
    app.include_router(healthcheck.router)
    for key, value in dispatcher.workflow_data.items():
        setattr(app.state, key, value)
    app.state.dispatcher = dispatcher
    app.state.bot = bot
    app.state.shutdown_completed = False
    return app
