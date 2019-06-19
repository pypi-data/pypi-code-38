import logging
import logging.config
import logging.handlers

from alv3_service.common.logformat import AL_LOG_FORMAT


def init_logging():
    logger = logging.getLogger('assemblyline')

    # Test if we've initialized the log handler already.
    if len(logger.handlers) != 0:
        return

    logging.root.setLevel(logging.CRITICAL)
    logger.setLevel(logging.INFO)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(AL_LOG_FORMAT))
    logger.addHandler(console)
