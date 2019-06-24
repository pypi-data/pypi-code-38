import logging.config

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": (
                    "%(asctime)s [%(levelname)s] [%(name)s] %(filename)s:"
                    "%(funcName)s:%(lineno)d | %(message)s"
                )
            }
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            }
        },
        "loggers": {
            "urllib3.connectionpool": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            }
        },
        "root": {"level": "DEBUG", "handlers": []},
    }
)
