import importlib
import logging
import sys
import traceback
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

from pyqalx.core.errors import QalxError


class QalxRotatingFileHandler(RotatingFileHandler):
    """
    We always force some defaults for a qalx logger
    """
    def __init__(self, *args, **kwargs):
        # 10 MB
        kwargs['maxBytes'] = kwargs.get('maxBytes', 10 * 1024 * 1024)
        kwargs['backupCount'] = kwargs.get('backupCount', 10)
        kwargs['mode'] = kwargs.get('mode', 'w')
        super(QalxRotatingFileHandler, self).__init__(*args, **kwargs)


class QalxLogFormatter(logging.Formatter):
    """
    Sometimes our log messages contain extra data.  Use this formatter to allow
    all handlers to use the same format while also handling the potential extra
    data
    """
    def __init__(self, style='%', *args, **kwargs):
        kwargs['fmt'] = '%(asctime)s %(name)-12s %(levelname)-8s ' \
                        '%(process)d %(message)s'
        super(QalxLogFormatter, self).__init__(*args, **kwargs)
        self.style = style
        self.original_style = self._style

    def format(self, record):
        dict_record = record.__dict__
        self._style = self.original_style
        if 'entity_type' in dict_record.keys() and \
                'entity_guid' in dict_record.keys():
            existing_format = self._style._fmt
            # Typically this is added if a user decorated function encounters
            # an unhandled exception
            existing_format += ' Entity Type: `%(entity_type)s`' \
                               ' Entity GUID: `%(entity_guid)s`'
            self._style = logging._STYLES[self.style][0](existing_format)
        return super(QalxLogFormatter, self).format(record)


def build_default_config(LEVEL, LOG_FILE_PATH):
    """
    Builds the default config for pyqalx.

    :param LEVEL: The level from the `LOGGING_LEVEL` variable in the
                  users config
    :param LOG_FILE_PATH: The path to the log file to be used when using
        `filehandler`
    :return: dict: The default config for pyqalx to use.
    """
    filehandler = {
        'class': 'pyqalx.core.log.QalxRotatingFileHandler',
        'filename': LOG_FILE_PATH,
        'formatter': 'default',
        'level': LEVEL
    }
    DEFAULT_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                '()': 'pyqalx.core.log.QalxLogFormatter',
                },
        },
        'handlers': {
            'nullhandler': {
                'class': 'logging.NullHandler',
                'level': LEVEL,
            },
            'filehandler': filehandler,
        },
        'loggers': {
            'pyqalx.core': {
                'handlers': ['filehandler'],
                'level': LEVEL
            },
            'pyqalx.bot': {
                'handlers': ['filehandler'],
                'level': LEVEL
            },
            'pyqalx.config': {
                'handlers': ['filehandler'],
                'level': LEVEL
            },
            'pyqalx.transport': {
                'handlers': ['filehandler'],
                'level': LEVEL
            },
            'pyqalx.integration': {
                'handlers': ['integration_filehandler'],
                'level': logging.INFO
            },
        },
    }
    DEFAULT_CONFIG['handlers']['integration_filehandler'] = filehandler
    # always log this as `info`.  This logger is so users can log to our
    # log files form their pyqalx implementation
    DEFAULT_CONFIG['handlers']['integration_filehandler']['level'] = logging.INFO
    return DEFAULT_CONFIG


def configure_logging(config):
    """
    Given a `Config` instance will attempt to get the configurable logging
    values from the profile - falling back to sensible defaults.
    It then configures the logger with our defaults and then overrides as
    necessary depending on if the user has specified a custom logging config
    :param config: An instance of `Config`
    """
    logging_config_func = dictConfig

    LOGGING_LEVEL = config.get('LOGGING_LEVEL').upper()  # noqa
    LOG_FILE_PATH = config.get('LOG_FILE_PATH')

    valid_levels = logging._levelToName.values()

    assert LOGGING_LEVEL in valid_levels, \
        'LOGGING_LEVEL must be one of ' \
        '{VALID_LEVELS}.  ' \
        'Value is {VALUE}'.format(VALID_LEVELS=', '.join(valid_levels),
                                  VALUE=LOGGING_LEVEL)

    LEVEL = getattr(logging, LOGGING_LEVEL.upper())

    logging_config_func(build_default_config(LEVEL=LEVEL,
                                             LOG_FILE_PATH=LOG_FILE_PATH))


def get_logger(exc_type, exc_value, exc_traceback):
    """
    From the unhandled exception (i.e. QalxError()) we build a
    TracebackException which we then inspect to determine the correct logger
    to log the error to
    """
    tb_exc = traceback.TracebackException(exc_type, exc_value, exc_traceback)
    path = tb_exc.stack[-1].filename
    loggers = [logging.getLogger(name) for name in
               logging.root.manager.loggerDict]
    # Assume anything that isn't internal is running as a bot from the
    # users side of things
    logger_name = 'pyqalx.bot'
    for logger in loggers:
        if logger.name.startswith('pyqalx') and logger.name != 'pyqalx.integration':
            # special case `pyqalx.integration`.  It isn't a module but we
            # need it so users can log themselves.
            module = importlib.import_module(logger.name)
            if module.__file__ == path:
                logger_name = logger.name
    return logging.getLogger(logger_name)


def exception_hook(exc_type, exc_value, exc_traceback, extra=None, logger=None):
    """
    We want to log any unhandled exception that occurs in pyqalx.  This
    includes `Qalx*` errors (i.e. because a user has misconfigured something)
    and also if they have made an error in one of their decorated functions
    (i.e. @bot.process).  This catches all errors and logs them and also
    prints out the traceback
    """
    if isinstance(exc_type(), QalxError):
        # Only handle `Qalx*` Errors.  We don't want to consume anything the
        # user has done wrong.  This will however handle issues with decorated
        # bot functions as these are caught in ~bot.Bot and handled as a
        # QalxError
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        if logger is None:
            logger = get_logger(exc_type, exc_value, exc_traceback)

        logger.error(msg="Qalx Exception:",
                     exc_info=(exc_type, exc_value, exc_traceback),
                     extra=extra)

        traceback.print_exception(exc_type, exc_value, exc_traceback, chain=False)
    else:
        # This is an exception elsewhere in the users codebase. We don' handle
        # it.  Just reraise it for the user to fix
        raise exc_type(exc_value)


sys.excepthook = exception_hook
