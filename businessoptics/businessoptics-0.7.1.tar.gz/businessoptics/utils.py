import functools
from collections import Mapping, Iterable, Sized
from itertools import islice
from time import sleep
import logging.config
from math import isnan

from datetime import datetime, date
import re
from decimal import Decimal

import boto3
from future.utils import reraise
import sys
from functools import reduce
from past.builtins import basestring

try:
    from numpy import bool_
except ImportError:
    bool_ = ()


def retry(num_attempts, exception_class, log):
    """
    Decorator which makes the given function retry
    up to num_attempts times each time it encounters
    an exception of type exception_class. Uses `log`
    to log warnings of failed attempts.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(num_attempts):
                try:
                    return func(*args, **kwargs)
                except exception_class as e:
                    if i == num_attempts - 1:
                        raise
                    else:
                        log.warn('Failed with error %r, trying again', e, extra={'stack': True})
                        sleep(1)

        return wrapper

    return decorator


def join_urls(*urls):
    """
    Join the given strings together, inserting / in between where necessary
    """
    return reduce(lambda url1, url2: url1.rstrip('/') + '/' + str(url2).lstrip('/'),
                  urls)


def add_exception_info(info):
    """
    Add the string info to the end of the message of the current exception while preserving the current traceback
    and also ensuring that the traceback shows the new information.
    Use with 'except Exception:' or something more specific, but not a bare except.
    Credit: http://stackoverflow.com/a/6062799/2482744
    """

    # Don't store the traceback (sys.exc_info()[2]) due to garbage collection problems:
    # see https://docs.python.org/2/library/sys.html#sys.exc_info
    exc_type, exc = sys.exc_info()[:2]
    reraise(exc_type, exc_type(str(exc) + "  \n  " + info), sys.exc_info()[2])


def strip_prefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    return string


try:
    from pandas import Timestamp
except ImportError:
    Timestamp = ()  # isinstance(x, ()) is always false


def fix_types(x):
    """
    Returns a version of x suitable for JSON serialisation and processing by the API.
    """
    if isinstance(x, Mapping):
        return {k: fix_types(v) for k, v in x.items()}
    elif isinstance(x, Iterable) and not isinstance(x, basestring):
        return [fix_types(y) for y in x]
    elif isinstance(x, (bool, bool_)):
        return int(x)
    elif isinstance(x, date):
        if not isinstance(x, datetime):
            x = datetime.combine(x, datetime.min.time())
        assert isinstance(x, datetime)
        return x.isoformat()
    elif isinstance(x, Timestamp):
        return x.isoformat()
    elif isinstance(x, Decimal):
        return float(x)
    elif isinstance(x, float) and isnan(x):
        return None
    else:
        return x


def ensure_list_if_string(x):
    if isinstance(x, basestring):
        x = list(filter(None, re.split('[,\s]+', x)))
    return x


def setup_quick_console_logging(debug=False):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s.%(msecs)03d %(levelname)8s | %(name)s.%(funcName)s:%(lineno)-4d | %(message)s',
                'datefmt': '%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'DEBUG' if debug else 'INFO',
            }
        }
    })


def only(it):
    """
    >>> only([7])
    7
    >>> only([1, 2])
    Traceback (most recent call last):
    ...
    AssertionError: Expected one value, found 2
    >>> only([])
    Traceback (most recent call last):
    ...
    AssertionError: Expected one value, found 0
    >>> from itertools import repeat
    >>> only(repeat(5))
    Traceback (most recent call last):
    ...
    AssertionError: Expected one value, found several
    >>> only(repeat(5, 0))
    Traceback (most recent call last):
    ...
    AssertionError: Expected one value, found 0
    """

    if isinstance(it, Sized):
        if len(it) != 1:
            raise AssertionError('Expected one value, found %s' % len(it))
        return it[0]

    lst = tuple(islice(it, 2))
    if len(lst) == 0:
        raise AssertionError('Expected one value, found 0')
    if len(lst) > 1:
        raise AssertionError('Expected one value, found several')
    return lst[0]


def boto3_client_from_credentials(service, credentials):
    return boto3.client(
        service,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )
