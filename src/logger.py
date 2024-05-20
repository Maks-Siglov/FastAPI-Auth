import logging

from core.settings import settings


def logger_config() -> None:
    logger = logging.getLogger("root")
    logger.setLevel(level=settings.log.level)
    handler = logging.StreamHandler()
    my_formatter = logging.Formatter(settings.log.ROOT_FORMATTER)
    handler.setFormatter(my_formatter)
    logger.addHandler(handler)
