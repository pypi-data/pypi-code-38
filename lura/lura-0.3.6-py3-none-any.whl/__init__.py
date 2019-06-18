from .log import Logging

logs = Logging(
  std_logger = __name__,
  std_format = Logging.formats.bare[0],
  std_datefmt = Logging.formats.bare[1],
)

del Logging
