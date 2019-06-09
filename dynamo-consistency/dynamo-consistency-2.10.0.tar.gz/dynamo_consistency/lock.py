"""
Performs simple file locking, and identifies which sites need which locks.
"""

import os
import fcntl

from . import config

def which(site):
    """
    Determine which lock is needed for a site from the config.
    For example, certain sites may require the ``gfal`` lock.

    :param str site: Site we want to lock for
    :returns: Name of the lock that should be acquired.
              If no lock to acquire, returns an empty string
    :rtype: str
    """

    method = config.config_dict().get('AccessMethod', {}).get(site)

    if method == 'SRM':
        return 'gfal'

    return ''


def acquire(lock):
    """
    This function will block until the named lock is acquired.
    The PID of the process using the lock is written to the lock file.
    The lock file is located inside of ``**VarLocation**/locks``

    :param str lock: Name of lock to acquire, which matches name in ``locks`` directory
    :returns: The filehandle to the lock. Don't loose it!
    :rtype: int
    """

    lock_dir = config.vardir('locks')

    lock_fh = open(os.path.join(lock_dir, '%s.lock' % lock), 'w', 0)
    fcntl.lockf(lock_fh, fcntl.LOCK_EX)
    lock_fh.write('%s\n' % os.getpid())

    return lock_fh


def release(lock_fh):
    """
    :param int lock_fh: File handle of lock to release
    """

    lock_fh.write('done\n')
    fcntl.lockf(lock_fh, fcntl.LOCK_UN)
    lock_fh.close()
