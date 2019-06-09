"""
Module the caches and holds the Site Readiness status

.. todo::

   Try to get the average uptime.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

import datetime
from .dashboard import GLOBAL_CACHE


def i_site_readiness(date=None):
    """Iterates over site readiness for the user

    :param datetime.date date: date
    :returns: iterator tuple with site, readiness, and drain status
    :rtype: generator
    """

    if date:
        if isinstance(date, (datetime.date, datetime.datetime)):
            info = GLOBAL_CACHE.get('ssb_237_{0:%d%m%y}'.format(date))
    else:
        info = GLOBAL_CACHE.get('ssb_237')


    for site_info in info:
        yield site_info['VOName'], site_info['COLORNAME'], site_info['Status']


def site_list():
    """Returns the list of sites

    :returns: The sorted list of site names
    :rtype: list
    """

    output = []

    for site, _, _ in i_site_readiness():
        output.append(site)

    output.sort()
    return output


def site_readiness(site_name, date=None):
    """Returns the readiness status for a given site

    :param datetime.date date: date
    :param str site_name: Name of the site
    :returns: Readiness status. Possibilities and their meanings are:
              - 'green': Ready
              - 'yellow': Waiting Room
              - 'red': Morgue
              - 'none': Site not found
    :rtype: str
    """
    for site, output, _ in i_site_readiness(date):
        if site == site_name:
            return output

    return 'none'


def site_drain_status(site_name):
    """Returns the drain status for a given site

    :param str site_name: Name of the site
    :returns: Readiness status. Possibilities and their meanings are:

              - 'enabled': The site is running
              - 'disabled': The site is not running
              - 'drain': The jobs at the site are being drained
              - 'test': This site is being commissioned or something?
              - 'none': Site not found

    :rtype: str
    """
    for site, _, output in i_site_readiness():
        if site == site_name:
            return output

    return 'none'


# This is something we want, but don't have
#
# def site_average_uptime(site_name, duration):
#     """Returns the average site readiness over the past duration (up to some value)
#     :param str site_name: Name of the site
#     :param float/int? duration: Amount of time to average over in day/weeks/months...
#     :returns: Average uptime in hours/days
#     :rtype: float
#     """
#     info = get_info()
#     return more complicated filter of info
