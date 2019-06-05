"""
    logging_setup.py

    Part of the hellofresh_data module meant to
    return a logger object in order to log various
    events.
"""
import logging


def init_logging(logger_name, loglevel=logging.DEBUG):
    """
        Creates standard logging for the logger_name passed in
    """

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    channel = logging.StreamHandler()
    channel.setLevel(loglevel)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    channel.setFormatter(formatter)

    logger.addHandler(channel)
    logger.debug("Initialized logging for %s", logger_name)

    return logger
