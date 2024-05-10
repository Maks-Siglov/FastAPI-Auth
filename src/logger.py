import logging

from core.settings import settings

ROOT_FORMATTER = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"


def logger_config() -> None:
    logger = logging.getLogger("root")
    logger.setLevel(level=settings.log.level)
    handler = logging.StreamHandler()
    my_formatter = logging.Formatter(ROOT_FORMATTER)
    handler.setFormatter(my_formatter)
    logger.addHandler(handler)
