import logging

from .config import log_level as __log_level
from .healthz import Healthz, HealthzStatus


def setup_logging():
    log_level = __log_level()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s:%(levelname)s:%(name)s -> %(message)s [%(filename)s:%(lineno)s]"
    )


__all__ = ['Healthz', 'setup_logging']
