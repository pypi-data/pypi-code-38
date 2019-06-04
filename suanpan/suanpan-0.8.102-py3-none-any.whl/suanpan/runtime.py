# coding=utf-8
from __future__ import absolute_import, print_function

import functools
import sys
import traceback

import retrying

from suanpan.log import logger


def needRetryException(exception):
    return not isinstance(exception, (KeyboardInterrupt, SystemExit))


def retryRunner(func):
    @functools.wraps(func)
    def _dec(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning("Run failed and retrying: {}".format(func.__name__))
            logger.warning(traceback.format_exc())
            raise e

    return _dec


def retry(*args, **kwargs):
    def _wrap(func):
        kwargs.update(wrap_exception=True, retry_on_exception=needRetryException)
        _retry = retrying.retry(*args, **kwargs)
        _func = _retry(retryRunner(func))

        @functools.wraps(func)
        def _dec(*fargs, **fkwargs):
            try:
                return _func(*fargs, **fkwargs)
            except retrying.RetryError as e:
                _, error, _ = e.last_attempt.value
                if needRetryException(error):
                    logger.error(
                        "Retry failed after {} attempts: {}".format(
                            e.last_attempt.attempt_number, func.__name__
                        )
                    )
                    raise e
                raise error

        return _dec

    return _wrap


def globalrun(func):
    @functools.wraps(func)
    def _dec(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            logger.debug("User canceled and exit 0.")
            sys.exit(0)
        except Exception as e:  # pylint: disable=broad-except
            logger.error(traceback.format_exc())
            raise e

    return _dec
