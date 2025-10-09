import logging
import sys

from app.models.config import AppConfig


def disable_aiogram_logs() -> None:
    """Отключает избыточные логи от aiogram"""
    for name in ["aiogram.middlewares", "aiohttp.access"]:
        logging.getLogger(name).setLevel(logging.WARNING)


def setup_logger(config: AppConfig | None = None, level: str | None = "INFO") -> None:
    """
    Настройка логгера

    Args:
        config: Конфигурация приложения
        level: Уровень логирования
    """

    # Получаем корневой логгер
    root_logger = logging.getLogger()

    # Очищаем существующие handlers, если они есть
    if root_logger.handlers:
        root_logger.handlers.clear()

    # Создаем консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s | %(name)s: %(message)s", datefmt="[%H:%M:%S]"
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)

    # Добавляем консольный handler
    root_logger.addHandler(console_handler)
    root_logger.setLevel(level)

    if config is None:
        return

    if level != "DEBUG":
        # Отключаем избыточные логи
        disable_aiogram_logs()

    logging.info("Logger setup successful")
