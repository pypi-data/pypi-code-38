import logging


def init_logger(logger_name=__name__, log_level=logging.DEBUG):
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
