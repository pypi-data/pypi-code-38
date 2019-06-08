"""aaypyutil

Usage:
------

    $ import aaypyutil

Contact:
--------

- https://aayushuppal.github.io

More information is available at:

- https://pypi.org/project/aaypyutil
- https://github.com/aayushuppal/aaypyutil
"""


import logging
import time
from functools import wraps


def retry_on_exception(ExceptionToCheck=Exception, tries=3, delay=2, backoff=2):
    """
    Retry calling the decorated function using an exponential backoff.
    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay each retry
    :type backoff: int
    """

    def deco_retry_on_exception(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay

            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "{}, Retrying in {} seconds...".format(str(e), mdelay)
                    logging.warning(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff

            return f(*args, **kwargs)

        return f_retry

    return deco_retry_on_exception
