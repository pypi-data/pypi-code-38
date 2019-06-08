import logging
import logging.config
import time

LOG_FORMAT = (
    "%(asctime)s - %(levelname)s %(name)s [%(process)d-%(thread)d]"
    + " %(filename)s:%(lineno)s  %(funcName)s - %(message)s"
)


class UTCFormatter(logging.Formatter):
    converter = time.gmtime


def configure_logger(log_file, console_level="WARN", file_level="DEBUG"):
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {"default": {"()": UTCFormatter, "format": LOG_FORMAT}},
            "handlers": {
                "console": {
                    "level": console_level,
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "file": {
                    "level": file_level,
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "formatter": "default",
                    "filename": log_file,
                    "utc": True,
                    "when": "midnight",
                    "encoding": "utf-8",
                    "backupCount": 3,
                },
            },
            "loggers": {"": {"handlers": ["console", "file"], "level": "DEBUG"}},
            "disable_existing_loggers": False,
        }
    )
