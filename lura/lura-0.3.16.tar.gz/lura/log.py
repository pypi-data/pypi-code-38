import logging
import logging.config
import os
import time
import types
from collections import defaultdict
from io import StringIO
from logging import NOTSET, DEBUG, INFO, WARNING, WARN, ERROR, CRITICAL, FATAL
from lura.attrs import attr
from lura.utils import DynamicProxy, asbool

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

class MultiLogger(DynamicProxy):

  NOTSET = logging.NOTSET
  DEBUG = logging.DEBUG
  INFO = logging.INFO
  WARNING = logging.WARNING
  WARN = logging.WARN
  ERROR = logging.ERROR
  CRITICAL = logging.CRITICAL
  FATAL = logging.FATAL

  def __init__(self, loggers):
    super().__init__(loggers)

class MultiLineFormatter(logging.Formatter):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def format(self, record):
    if os.linesep not in record.msg:
      record.message = super().format(record)
      return record.message
    msg = record.msg
    with StringIO() as buf:
      for line in record.msg.split(os.linesep):
        record.msg = line
        buf.write(super().format(record) + os.linesep)
      record.message = buf.getvalue().rpartition(os.linesep)[0]
      #record.message = buf.getvalue().rstrip(os.linesep)
    record.msg = msg
    return record.message

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
      '%(run_time)-8.3f %(short_name)19s %(short_levelname)s %(message)s',
      '%Y-%m-%d %H:%M:%S',
    ),

    # More verbose and longer field width.
    debuglong = (
      '%(run_time)-12.3f %(name)25s %(short_levelname)s %(message)s',
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
    self.config = None
    self.configure()

  def configure(self):
    if self.config is not None:
      return
    self.config_logging()
    self.config_levels()
    self.config_environment()

  def config_logging(self):
    self.config = self.build_config()
    logging.config.dictConfig(self.config)
    for level, name in logging._levelToName.items():
      setattr(logging.Logger, name, level)

  def config_levels(self):
    if 'NOISE' not in logging._levelToName.values():
      self.add_level('NOISE', 5, ':')

  def config_environment(self):
    if self.level_envvar in os.environ:
      self.set_level(os.environ[self.level_envvar].upper())
    if self.log_envvar in os.environ:
      file = os.environ[self.log_envvar]
      append = asbool(os.environ.get(self.append_envvar, '0'))
      level = os.environ.get(self.level_envvar, self.get_level())
      handler = self.add_file_handler(file, level=level, append=append)
      handler.set_name(self.log_envvar)
      fmt = os.environ.get(self.format_envvar, 'verbose').lower()
      handler.setFormatter(MultiLineFormatter(*self.formats[fmt]))

  def build_config(self):
    import yaml
    config = yaml.safe_load(f'''
      version: 1
      filters:
        short_name: {{}}
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
    ''')
    config['filters']['short_name']['()'] = ExtraInfoFilter
    config['formatters']['standard']['()'] = MultiLineFormatter
    return config

  def build_logger_log_method(self, level):
    def log_level(self, msg, *args, **kwargs):
      if self.isEnabledFor(level):
        self._log(level, msg, args, **kwargs)
    return log_level

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

  def get_level(self):
    'Get standard logger log level.'

    return self.get_logger(self.std_logger).getEffectiveLevel()

  def set_level(self, level):
    'Set standard logger log level.'

    if isinstance(level, str):
      level = getattr(self, level)
    self.get_logger(self.std_logger).setLevel(level)
    if level in (self.DEBUG, self.NOISE):
      self.set_formats('debug', self.std_logger)

  def get_level_name(self, number):
    return logging._levelToName[number]

  def add_level(self, name, number, short_name=None):
    if number in logging._levelToName.keys():
      msg = 'Log level number {} already used by {}'
      raise ValueError(msg.format(number, self.get_level_name(number)))
    elif name in logging._levelToName.values():
      raise ValueError(f'Log level name {name} already in use')
    logging.addLevelName(number, name)
    setattr(logging, name, number)
    setattr(logging.Logger, name, number)
    setattr(MultiLogger, name, number)
    setattr(type(self), name, number)
    setattr(
      logging.Logger, name.lower(), self.build_logger_log_method(number))
    if short_name is not None:
      ExtraInfoFilter.map_short_level[name] = short_name

  def set_format(self, format, datefmt, logger=None):
    '''
    Set the format for all handlers of a logger.

    :param str format: log format specification
    :param str datefmt: date format specification
    '''
    logger = self.std_logger if logger is None else logger
    logger = self.get_logger(logger)
    formatter = MultiLineFormatter(format, datefmt)
    for _ in logger.handlers:
      if _.get_name() == self.log_envvar:
        continue
      _.setFormatter(formatter)

  def set_formats(self, format, logger=None):
    logger = self.std_logger if logger is None else logger
    self.set_format(*self.formats[format], logger)

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
      if isinstance(level, str):
        level = getattr(self, level)
      handler.setLevel(level)
    formatter = MultiLineFormatter(*self.formats.verbose)
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

  def multilog(self, *loggers):
    'Log messages to multiple loggers.'

    return MultiLogger([_ for _ in loggers if _])
