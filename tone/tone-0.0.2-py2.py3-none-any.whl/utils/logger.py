# coding=utf-8
import logging
import logging.config


def get_basic_logger(name='tone'):
    '''
    Get logger for convenient method
    '''

    logger = logging.getLogger(name)
    if len(logger.handlers) > 0:
        return logger

    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '[%(asctime)s] [%(module)s] [%(lineno)d] [%(levelname)s] | %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                "level": "DEBUG",
            },
        },
        'loggers': {
            name: {
                'handlers': ['console', ],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }
    logging.config.dictConfig(config)
    logger = logging.getLogger(name)
    return logger


def get_logger(name='tone'):
    return get_basic_logger(name)
