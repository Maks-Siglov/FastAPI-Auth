import logging

from src.core.settings import log_settings


def logger_config() -> None:
    logger = logging.getLogger("root")
    logger.setLevel(level=log_settings.level)
    handler = logging.StreamHandler()
    my_formatter = logging.Formatter(log_settings.ROOT_FORMATTER)
    handler.setFormatter(my_formatter)
    logger.addHandler(handler)
