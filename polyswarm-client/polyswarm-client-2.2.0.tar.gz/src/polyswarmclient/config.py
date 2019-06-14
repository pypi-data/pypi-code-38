import click
import logging
import string

from polyswarmclient.log_formatter import JSONFormatter, ExtraTextFormatter

logger = logging.getLogger(__name__)


def validate_apikey(ctx, param, value):
    """Validates the API key passed in through click parameters"""
    try:
        # If we received the parameter's default value, then don't bother checking.
        if value == param.get_default(ctx):
            return value
        # Verify we have a hex-clean API key which of the appropriate length.
        if len(value) != 32 or not all([c in string.hexdigits.lower() for c in value]):
            raise click.BadParameter("API key is an invalid 16-byte hex value.")
        return value
    except ValueError:
        raise click.BadParameter("API key must only contain valid hexadecimal values")
    except TypeError:
        # I don't believe this can ever be triggered as a click option, but I'm keeping it around for completeness.
        raise click.BadParameter("API key must be a string")


def init_logging(loggers, log_format, loglevel=logging.WARNING):
    """
    Logic to support JSON logging.
    """
    # Change settings on polyswarm-client logger
    logger_config = LoggerConfig(loggers, log_format, loglevel)
    logger_config.configure()


class LoggerConfig:
    LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

    def __init__(self, loggers, log_format, log_level=logging.WARNING):
        self.loggers = loggers
        self.log_format = log_format
        self.log_level = log_level

    def configure(self):
        for name in self.loggers:
            logger = logging.getLogger(name)
            if self.log_format and self.log_format in ['json', 'datadog']:
                log_handler = logging.StreamHandler()
                formatter = JSONFormatter('(level) (name) (timestamp) (message)')
                log_handler.setFormatter(formatter)
                logger.addHandler(log_handler)
                logger.setLevel(self.log_level)
                logger.info("Logging in JSON format.")
            else:
                log_handler = logging.StreamHandler()
                log_handler.setFormatter(ExtraTextFormatter(fmt='%(levelname)s:%(name)s:%(asctime)s %(message)s'))
                logger.addHandler(log_handler)
                logger.setLevel(self.log_level)
                logger.info("Logging in text format.")

    def set_level(self, new_level):
        self.log_level = new_level
        for name in self.loggers:
            logger = logging.getLogger(name)
            logger.setLevel(self.log_level)
