import logging
from logging.handlers import RotatingFileHandler

MAX_LOG_SIZE = 1024 * 1024
LOG_BACKUP_COUNT = 3


def setup_logging():
    """Настройка логирования операций"""
    logger = logging.getLogger("valutatrade")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = RotatingFileHandler(
            "logs/actions.log",
            maxBytes=MAX_LOG_SIZE,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8"
            )
        formatter = logging.Formatter(
            "%(levelname)s %(asctime)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S"
            )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger