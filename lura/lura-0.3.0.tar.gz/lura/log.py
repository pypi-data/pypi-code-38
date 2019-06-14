import logging
import logging.config
import os
import time
import types
from collections import defaultdict
from logging import NOTSET, DEBUG, INFO, WARNING, WARN, ERROR, CRITICAL, FATAL
from lura.attrs import attr
from lura.utils import asbool

class ExtraInfoFilter(logging.Filter):
  '''
  Provides additional fields to log records:

  - ``short_name`` a reasonably short name
  - ``shortest_name`` the shortest reasonably useful name
  - ``short_levelname`` a symbol associated with a level
  - ``run_time`` number of seconds the logging system has been initialized
  '''

  initialized = time.time()

  map_short_level = defaultdict(
    lambda: '=',
    DEBUG    = '+',
    INFO     = '|',
    WARNING  = '>',
    ERROR    = '*',
    CRITICAL = '!',
  )

  def filter(self, record):
    _ = record.name.split('.')
    record.short_name = '.'.join(_[-2:])
    record.shortest_name = _[-1]
    record.short_levelname = self.map_short_level.get(record.levelname)
    record.run_time = time.time() - self.initialized
    return True

class Logging:

  NOTSET = logging.NOTSET
  DEBUG = logging.DEBUG
  INFO = logging.INFO
  WARNING = logging.WARNING
  WARN = logging.WARN
  ERROR = logging.ERROR
  CRITICAL = logging.CRITICAL
  FATAL = logging.FATAL

  # Custom log formats.
  formats = attr(

    # Only the log message.
    bare = (
      '%(message)s',
      '%Y-%m-%d %H:%M:%S',
    ),

    # More old-school.
    classic = (
      '%(asctime)s %(levelname)-8s %(short_name)s %(message)s',
      '%Y-%m-%d %H:%M:%S',
    ),

    # More verbose.
    debug = (
      '%(run_time)-12.3f %(short_name)20s %(short_levelname)s %(message)s',
      '%Y-%m-%d %H:%M:%S',
    ),

    # Run time and message.
    runtime = (
      '%(run_time)-12.3f %(message)s',
      '%Y-%m-%d %H:%M:%S',
    ),

    # Very long.
    verbose = (
      '%(asctime)s %(run_time)12.3f %(name)s %(short_levelname)s %(message)s',
      '%Y-%m-%d %H:%M:%S',
    ),
  )

  def __init__(
    self,
    std_logger,
    std_format = None,
    std_datefmt = None,
    log_envvar = None,
    level_envvar = None,
    format_envvar = None,
    append_envvar = None,
  ):
    super().__init__()
    self.std_logger = std_logger
    if std_format is None:
      std_format = self.formats.bare[0]
    if std_datefmt is None:
      std_datefmt = self.formats.bare[1]
    stdup = std_logger.upper()
    if log_envvar is None:
      log_envvar = f'{stdup}_LOG'
    if level_envvar is None:
      level_envvar = f'{stdup}_LOG_LEVEL'
    if format_envvar is None:
      format_envvar = f'{stdup}_LOG_FORMAT'
    if append_envvar is None:
      append_envvar = f'{stdup}_LOG_APPEND'
    self.std_format = std_format
    self.std_datefmt = std_datefmt
    self.log_envvar = log_envvar
    self.level_envvar = level_envvar
    self.format_envvar = format_envvar
    self.append_envvar = append_envvar
    self.configured = False
    self.configure()

  def build_config(self):
    from lura.fmt import yaml
    self.config = yaml.loads(
      f'''
      version: 1
      filters:
        short_name:
      formatters:
        standard:
          format: '{self.std_format}'
          datefmt: '{self.std_datefmt}'
      handlers:
        stderr:
          class: logging.StreamHandler
          stream: ext://sys.stderr
          filters: ['short_name']
          formatter: standard
      loggers:
        {self.std_logger}:
          handlers: ['stderr']
          level: INFO
      '''
    )
    self.config.filters.short_name = {'()': ExtraInfoFilter}

  def configure(self):
    assert(not self.configured)
    self.build_config()
    logging.config.dictConfig(self.config)
    if self.log_envvar not in os.environ:
      return
    file = os.environ[self.log_envvar]
    level = os.environ.get(self.level_envvar, 'DEBUG')
    level = getattr(logging, level)
    append = asbool(os.environ.get(self.append_envvar, '0'))
    handler = self.add_file_handler(file, level=level, append=append)
    handler.set_name(self.log_envvar)
    fmt = os.environ.get(self.format_envvar, 'verbose').lower()
    handler.setFormatter(logging.Formatter(*self.formats[fmt]))
    self.configured = True

  def add_level(self, name, number, short_name=None):
    def log_custom(self, msg, *args, **kwargs):
      if self.isEnabledFor(number):
        self._log(number, msg, args, **kwargs)
    logging.addLevelName(number, name)
    setattr(logging, name, number)
    setattr(type(self), name, number)
    setattr(logging.Logger, name.lower(), log_custom)
    if short_name is not None:
      ExtraInfoFilter.map_short_level[name] = short_name

  def get_logger(self, obj=None):
    if obj is None:
      name = self.std_logger
    elif isinstance(obj, str):
      name = obj
    elif isinstance(obj, type):
      name = f'{obj.__module__}.{obj.__name__}'
    else:
      name = f'{obj.__module__}.{type(obj).__name__}'
    return logging.getLogger(name)

  getLogger = get_logger

  def set_format(self, format, datefmt, logger=None):
    '''
    Set the format for all handlers of a logger.

    :param str format: log format specification
    :param str datefmt: date format specification
    '''
    logger = self.std_logger if logger is None else logger
    logger = self.get_logger(logger)
    formatter = logging.Formatter(format, datefmt)
    for _ in logger.handlers:
      if _.get_name() == self.log_envvar:
        continue
      _.setFormatter(formatter)

  def set_formats(self, format, logger=None):
    logger = self.std_logger if logger is None else logger
    self.set_format(*self.formats[format], logger)

  def get_level(self, logger=None):
    'Get logger log level.'

    logger = self.std_logger if logger is None else logger
    return self.get_logger(logger).getEffectiveLevel()

  def set_level(self, level, logger=None):
    'Set root logger log level.'

    if isinstance(level, str):
      level = getattr(self, level)
    logger = self.std_logger if logger is None else logger
    self.get_logger(logger).setLevel(level)
    if level in (self.DEBUG, self.NOISE):
      self.set_formats('debug', logger)

  def get_level_name(self, number):
    return logging._levelToName[number]

  def add_file_handler(self, path, level=None, logger=None, append=True):
    '''
    Add a file handler to write log messages to a file.

    :param [str, stream] path: path to log file or a stream
    :param int level: logging level, or None to defer
    :param str logger: name of logger to receive the file handler
    :param bool append: if True, append to existing log, if False, overwrite it
    :returns: the file handler, for use with ``remove_handler()``
    :rtype: logging.FileHandler
    '''
    logger = self.std_logger if logger is None else logger
    if isinstance(path, str):
      if not append and os.path.isfile(path):
        os.unlink(path)
      handler = logging.FileHandler(path)
    else:
      handler = logging.StreamHandler(path)
    if level is not None:
      handler.setLevel(level)
    formatter = logging.Formatter(*self.formats.verbose)
    handler.setFormatter(formatter)
    handler.addFilter(ExtraInfoFilter())
    self.get_logger(logger).addHandler(handler)
    return handler

  def remove_handler(self, handler, logger=None):
    '''
    Remove a handler from a logger.

    :param logging.Handler handler: handler instance to remove
    :param str logger: name of logger for removal
    '''
    logger = self.std_logger if logger is None else logger
    self.get_logger(logger).removeHandler(handler)

logs = Logging(
  std_logger = __name__.split('.')[0],
  std_format = Logging.formats.bare[0],
  std_datefmt = Logging.formats.bare[1],
)
logs.add_level('NOISE', 5, short_name=':')
