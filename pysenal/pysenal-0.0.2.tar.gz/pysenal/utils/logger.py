# -*- coding: UTF-8 -*-
import sys
import logging


def get_logger(name, handler=logging.StreamHandler(sys.stderr), level=logging.DEBUG):
    """
    encapsulate get logger operation
    :param name: logger name
    :param handler: logger handler, default is stderr
    :param level: logger level, default is debug
    :return: logger
    """
    logger = logging.getLogger(name)
    handler.setFormatter(logging.Formatter('[%(asctime)s] [{}] %(message)s'.format(name)))
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
