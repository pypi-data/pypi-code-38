import logging
from logging import DEBUG, INFO, WARNING, ERROR  # noqa: F401

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-7s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)

logger = logging.getLogger('timedata')
setLevel = logger.setLevel

debug, info, warning, error, fatal = (
    logger.debug,
    logger.info,
    logger.warning,
    logger.error,
    logger.fatal,
)

# The function `printer` emits text no matter what the loglevel, and without
# any # introducers like "INFO".  By default this is the same as the global
# `print` - # re-assign this variable if you need to redirect your printing.
printer = print  # noqa: T001, T002
