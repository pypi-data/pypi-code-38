import logging
import logging.config
import logging.handlers
from sys import stdout
from cached_property import cached_property
from egcg_core.config import cfg


class LoggingConfiguration:
    """Stores Loggers, Formatters and Handlers"""

    default_fmt = '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
    default_datefmt = '%Y-%b-%d %H:%M:%S'

    def __init__(self, config):
        self.cfg = config
        self.blank_formatter = logging.Formatter()
        self.handlers = set()
        self.loggers = {}
        self._log_level = logging.INFO

    @cached_property
    def formatter(self):
        return self.default_formatter

    @cached_property
    def default_formatter(self):
        return logging.Formatter(
            fmt=self.cfg.get('format', self.default_fmt),
            datefmt=self.cfg.get('datefmt', self.default_datefmt)
        )

    def get_logger(self, name, level=logging.NOTSET):
        """
        Return a logging.Logger object with formatters and handlers added.
        :param name: Name to assign to the logger (usually __name__)
        :param int level: Log level to assign to the logger upon creation
        """
        if name in self.loggers:
            logger = self.loggers[name]
        else:
            logger = logging.getLogger(name)
            self.loggers[name] = logger

        logger.setLevel(level or self._log_level)
        for h in self.handlers:
            logger.addHandler(h)

        return logger

    def add_handler(self, handler, level=logging.NOTSET):
        """
        Add a created handler, set its format/level if needed and register all loggers to it
        :param logging.Handler handler:
        :param int level: Log level to assign to the created handler
        """
        handler.setLevel(level or self._log_level)
        handler.setFormatter(self.formatter)
        for name in self.loggers:
            self.loggers[name].addHandler(handler)
        self.handlers.add(handler)

    def add_stdout_handler(self, level=logging.INFO):
        self.add_handler(logging.StreamHandler(stdout), level=level)

    def set_log_level(self, level):
        self._log_level = level
        for h in self.handlers:
            h.setLevel(self._log_level)
        for name in self.loggers:
            self.loggers[name].setLevel(self._log_level)

    def set_formatter(self, formatter):
        """
        Set all handlers to use formatter
        :param logging.Formatter formatter:
        """
        self.__dict__['formatter'] = formatter
        for h in self.handlers:
            h.setFormatter(self.formatter)

    def configure_handlers_from_config(self):
        configurator = logging.config.BaseConfigurator({})
        handler_classes = {
            'stream_handlers': logging.StreamHandler,
            'file_handlers': logging.FileHandler,
            'timed_rotating_file_handlers': logging.handlers.TimedRotatingFileHandler
        }

        for handler_type in handler_classes:
            for handler_cfg in self.cfg.get(handler_type, []):
                level = logging.getLevelName(handler_cfg.pop('level', self._log_level))

                if 'stream' in handler_cfg:
                    handler_cfg['stream'] = configurator.convert(handler_cfg['stream'])
                handler = handler_classes[handler_type](**handler_cfg)
                self.add_handler(handler, level)

    def reset(self):
        for l in self.loggers.values():
            while l.handlers:
                l.removeHandler(l.handlers[0])

        while self.handlers:
            h = self.handlers.pop()
            del h


logging_default = LoggingConfiguration(cfg)


class AppLogger:
    """
    Mixin class for logging. An object subclassing this can log using its class name. Contains a
    logging.Logger object and exposes its log methods.
    """
    log_cfg = logging_default

    def debug(self, msg, *args):
        self._logger.debug(msg, *args)

    def info(self, msg, *args):
        self._logger.info(msg, *args)

    def warning(self, msg, *args):
        self._logger.warning(msg, *args)

    def error(self, msg, *args):
        self._logger.error(msg, *args)

    def critical(self, msg, *args):
        self._logger.critical(msg, *args)

    @cached_property
    def _logger(self):
        return self.log_cfg.get_logger(self.__class__.__name__)
