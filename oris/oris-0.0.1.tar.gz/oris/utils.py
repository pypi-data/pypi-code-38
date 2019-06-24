"""Utility classes."""

import logging
import sys

log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


def logging_at(level):
    """Check if logging is enabled at the given level."""

    return logging.getLogger().isEnabledFor(getattr(logging, level.upper()))


def set_logging(level='WARNING', out=sys.stderr):
    """Set the log level and output."""

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=getattr(logging, level.upper()),
                        stream=out,
                        format=('[%(asctime)s] '
                                '(%(module)s.%(funcName)s#%(lineno)s) '
                                '%(levelname)s: %(message)s'))
