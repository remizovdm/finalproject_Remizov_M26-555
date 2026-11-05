import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger("valutatrade")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = RotatingFileHandler(
            "logs/actions.log",
            maxBytes=1024 * 1024,
            backupCount=3,
            encoding="utf-8"
            )
        formatter = logging.Formatter(
            "%(levelname)s %(asctime)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S"
            )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger