

import logging
from functools import lru_cache


DEFAULT_LEVEL = logging.DEBUG
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_FORMAT = '{asctime} [{levelname:>9}] {message} - ({filename}:{lineno:04})'
DEFAULT_FORMAT_STYLE = '{'


@lru_cache(maxsize=10)
def get_logger(level=logging.NOTSET):
    """Get a standardized logger object."""
    logger = logging.getLogger(__name__)
    logger.setLevel(DEFAULT_LEVEL)
    logger.addHandler(get_stream_handler())
    return logger


def get_formatter(fmt=DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT, style=DEFAULT_FORMAT_STYLE):
    """Obtain a default formatter."""
    return logging.Formatter(fmt=fmt, datefmt=datefmt, style=style)


def get_stream_handler(formatter=None):
    """Obtain a default stream handler."""
    if formatter is None:
        formatter = get_formatter()
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    return stream_handler
