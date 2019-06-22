import logging
from openProduction.common import misc

def initLogger():
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(misc.getAppName())
    logger.setLevel(logging.DEBUG)
    
    if len(logger.handlers) == 0:
        logger.addHandler(handler)
    return logger