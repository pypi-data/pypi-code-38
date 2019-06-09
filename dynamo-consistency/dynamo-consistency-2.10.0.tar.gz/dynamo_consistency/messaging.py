"""
A module for handling messages
"""

import time

from . import config
from . import lock
from .summary import _connect


class Killed(Exception):
    """
    An exception to throw when no longer running a site
    """
    pass


class Checker(object):
    """
    Checks the summary every few seconds if it should still be running

    :param str site: Site to check. If none, read from ``config.SITE``
    :param int timeout: Number of seconds between checks to summary table
    :param bool locking: True to get a lock before reading the database.
                         This is mostly to avoid agressive reading.
    """

    def __init__(self, site=None, timeout=15, locking=True):
        # Make sure a false value doesn't slip in there
        self.last = time.time() - 2 * timeout or 1
        self.timeout = timeout
        self.site = site or config.SITE
        self.lock = locking

    def isrunning(self):
        """
        :returns: If the site given is supposed to be running
        :rtype: bool
        """

        if self.site and self.last + self.timeout < time.time():

            if self.lock:
                self.lock = lock.acquire('summary')

            try:
                conn = _connect()
                curs = conn.cursor()

                curs.execute('SELECT isrunning FROM sites WHERE site = ?',
                             (self.site,))

                res = curs.fetchone()
                self.last = time.time() if res and res[0] > 0 else 0
                conn.close()

            finally:
                if self.lock:
                    lock.release(self.lock)

        return bool(self.last)
