DEFAULT_LOGGING = {
    "version": 1,
    "formatters": {
        "long": {
            "format": "%(asctime)-24s %(levelname)-8s [%(name)s] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "long",
            "stream": "ext://sys.stdout"
        },
        "loop_stderr": {
            "class": "logging.StreamHandler",
            "formatter": "long",
            "stream": "ext://sys.stderr",
            "level": "ERROR"
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO"
    },
    "loggers": {
        "asyncio": {
            "handlers": ["loop_stderr"],
            "level": "WARNING"
        },
        "hbmqtt": {
            "level": "WARNING"
        },
        "slixmpp": {
            "level": "WARNING"
        },
        "websockets": {
            "level": "WARNING"
        }
    },
    "disable_existing_loggers": False
}
