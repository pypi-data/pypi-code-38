import logging

from .version import __version__

name = "td_pyspark"

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


__all__ = [
    '__version__'
]
