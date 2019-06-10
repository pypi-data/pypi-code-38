"""
The bit of the summary table that also relies on accurate backend.
"""

import logging
import re

from . import lock
from . import config

from .summary import _connect
from .summary import NoMatchingSite

from .backend import siteinfo
from .backend import check_site


LOG = logging.getLogger(__name__)


def pick_site(pattern=None, lockname=None):
    """
    This function also does the task of syncronizing the summary database with
    the inventory's list of sites that match the pattern.

    :param str pattern: A regex that needs to be contained in the site name
    :param str lockname: Name of the lock file that the site should use.
                         Needs to be `''` for guaranteed no lock.
    :returns: The name of a site that is ready and hasn't run in the longest time
    :rtype: str
    :raises NoMatchingSite: If no site matches or is ready
    """

    # First add sites that match our pattern
    sites = siteinfo.site_list()
    if pattern:
        sites = [site for site in sites if re.search(pattern, site)]

    if not sites:
        raise NoMatchingSite('Cannot find a site that matches %s' % pattern)

    conn = _connect()
    curs = conn.cursor()

    curs.executemany(
        'INSERT OR IGNORE INTO sites VALUES (?, 0, 0, NULL)',
        [(site,) for site in sites]
        )

    # Now get the one that hasn't run in the longest time, and is good

    sites = set(sites)

    output = None

    # Track not ready sites so we can update the web view
    not_ready = []

    LOG.debug('Potential sites: %s', sites)

    for site, isrunning in curs.execute(
            """
            SELECT sites.site, isrunning FROM sites
            LEFT JOIN stats ON sites.site=stats.site
            ORDER BY stats.entered ASC, sites.site ASC
            """):
        LOG.debug('Considering %s (run status %s)', site, isrunning)
        if site in sites and \
                (isrunning == 0 or isrunning == -1) and \
                (lockname is None or (lock.which(site) == lockname)):
            if check_site(site):
                output = site
                break
            else:
                not_ready.append(site)

    curs.executemany('UPDATE sites SET isrunning = -1 WHERE site = ?',
                     [(site,) for site in not_ready])

    # Lock selected site
    if output is not None:
        curs.execute('UPDATE sites SET isrunning = 1 WHERE site = ?', (output,))

    conn.commit()
    conn.close()

    if output is None:
        raise NoMatchingSite('No sites out of %s seem to be ready' % sites)

    # Log the pid that will run on this site
    # Only logging, so don't hold the lock
    lock.release(lock.acquire(output))

    config.SITE = output

    return output
