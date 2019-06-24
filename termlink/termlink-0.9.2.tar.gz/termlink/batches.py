"""A utility for iterating in batches.

This module provides utility methods for iterating over iterables in batches.
"""

import time

from termlink.configuration import Config

_configuration = Config()
_logger = _configuration.logger

_DEFAULT_RATE_LIMIT = 10
_DEFAULT_RATE_LIMIT_PERIOD = 1

_rate_limit = int(_configuration.get_property('API_RATE_LIMIT', _DEFAULT_RATE_LIMIT))
_rate_limit_period = int(_configuration.get_property('API_RATE_LIMIT_PERIOD', _DEFAULT_RATE_LIMIT_PERIOD))


def batch(iterable, n=1, sleep=_rate_limit_period):
    """
    Traverses over an iterable in batches of size n sleeping :sleep: seconds
    between batches.

    Args:
        iterable:   An iterable
        n:          Size of each batch
        sleep:      Number of seconds to sleep between batches

    Returns:
        For each batch, yields a batch of size n, len(iterable) % n times
    """

    limit = n / (_rate_limit)
    sleep = sleep if 0 < sleep < limit else limit
    _logger.info("sleep set to %f seconds", sleep)

    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx : min(ndx + n, l)]
        _logger.info("Processed %s of %s", min(ndx + n, l), l)
        time.sleep(sleep)
