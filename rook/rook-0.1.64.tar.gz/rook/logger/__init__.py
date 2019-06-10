import sys
import json

from rook.config import LoggingConfiguration

from .logger_factory import LoggerFactory
from .logging_types import LogType
from .kw_log import KWLogger

try:
    # This makes our internal errors not appear in sentry
    from sentry_sdk.integrations.logging import ignore_logger
    ignore_logger('rook')
except ImportError:
    pass


def logger_with_metadata(*extra_tags):
    return KWLogger(_base_logger, list(extra_tags))


def _build_logger():
    log_level = LoggingConfiguration.LOG_LEVEL
    log_to_stderr = LoggingConfiguration.LOG_TO_STDERR

    if 'unittest' in sys.argv[0]:
        log_level = 10
        log_to_stderr = True

    return LoggerFactory(
        LoggingConfiguration.LOGGER_NAME,
        log_level,
        LoggingConfiguration.FILE_NAME,
        log_to_stderr,
        LoggingConfiguration.LOG_TO_REMOTE,
        LoggingConfiguration.PROPAGATE_LOGS
    ).get_logger()


logger_parmas = dict(
    name=LoggingConfiguration.LOGGER_NAME,
    log_level=LoggingConfiguration.LOG_LEVEL,
    file_name=LoggingConfiguration.FILE_NAME,
    stderr=LoggingConfiguration.LOG_TO_STDERR,
    log_to_remote=LoggingConfiguration.LOG_TO_REMOTE,
    propagate_logs=LoggingConfiguration.PROPAGATE_LOGS)
_base_logger = _build_logger()
logger = KWLogger(_base_logger)
logger.info("Initialized logger")
logger.info("Logger params: {}".format(json.dumps(logger_parmas)))
