import logging
from logging.handlers import RotatingFileHandler

from pathlib import Path
from typing import Optional

LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s:%(message)s'
DATE_FORMAT = '%d-%b-%Y %H:%M:%S'


def setupPeekLogger(serviceName: Optional[str] = None):
    logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT, level=logging.DEBUG)

    if serviceName:
        # Add a logger to file
        fileName = str(Path.home() / ('%s.log' % serviceName))

        logFormatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        rootLogger = logging.getLogger()

        fh = RotatingFileHandler(fileName, maxBytes=(1024 * 1024 * 20), backupCount=2)
        fh.setFormatter(logFormatter)
        rootLogger.addHandler(fh)
