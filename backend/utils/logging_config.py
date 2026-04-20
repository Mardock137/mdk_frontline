"""Centralized logging configuration (console + rotating file)."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from utils.config import BACKEND_DIR, get_settings

LOGS_DIR = BACKEND_DIR / "logs"
LOG_FILE = LOGS_DIR / "backend.log"

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 5


def setup_logging(log_level: str | None = None, log_file: Path | None = None) -> logging.Logger:
    """Configure the root logger with console and rotating file handlers.

    Idempotent: repeated calls replace existing handlers instead of stacking them.
    """
    settings = get_settings()
    level_name = (log_level or settings.LOG_LEVEL).upper()
    level = getattr(logging, level_name, logging.INFO)

    target_file = log_file or LOG_FILE
    target_file.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        target_file,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    return root_logger
