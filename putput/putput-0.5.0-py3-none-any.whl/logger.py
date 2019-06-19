import logging
import sys
from typing import IO


def get_logger(module_name: str, *, level: int = logging.INFO, stream: IO[str] = sys.stderr) -> logging.Logger:
    """Returns a configured logger for the module.

    Args:
        module_name: __name__ for the calling module.

        level: Minimum logging level. Messages with this level or
            higher will be shown.

        stream: 'stream' argument to logging.StreamHandler, typically sys.stdout or sys.stderr.

    Raises:
        ValueError: If stream is not 'stderr' or 'stdout'.
    """
    logger = logging.getLogger(module_name)
    if not logger.handlers:
        logger.propagate = False
        logger.setLevel(level)

        stream_handler = logging.StreamHandler(stream)
        stream_handler.setLevel(level)

        handler_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(handler_format)
        stream_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)
    return logger
