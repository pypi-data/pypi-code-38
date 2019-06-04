import os
import logging

LOG_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'silly': 0
}
log_level_key = os.environ.get('LOG_LEVEL', LOG_LEVELS['silly'])
log_level = LOG_LEVELS.get(log_level_key, LOG_LEVELS['silly'])

logger = logging.getLogger()
logger.setLevel(log_level)