import os
import logging
import logging.config

from metagenomi.config import (BASE_DIR, LOGFILE)


logfmt = "[%(asctime)s] %(levelname)s [%(filename)s->" \
    "%(funcName)s:%(lineno)s] %(message)s"

LOG_CONFIG = {
    "version": 1,
    'formatters': {
        'standard': {
            'format': logfmt,
            'datefmt': "%Y/%m/%d %H:%M:%S"
        },
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, LOGFILE),
            'maxBytes': 2097152,  # 2MB per file
            'backupCount': 2,  # Store up to three files
            'formatter': 'standard',
        },
    },
    'loggers': {
        'metagenomi': {
            'handlers': ["logfile", ],
            'level': 'DEBUG',
        },
    }
}

logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger("metagenomi")
