import logging

from src.settings import LogSettings


def logger_config() -> None:
    logger = logging.getLogger("root")
    logger.setLevel(level=LogSettings.level)
    handler = logging.StreamHandler()
    my_formatter = logging.Formatter(LogSettings.ROOT_FORMATTER)
    handler.setFormatter(my_formatter)
    logger.addHandler(handler)
