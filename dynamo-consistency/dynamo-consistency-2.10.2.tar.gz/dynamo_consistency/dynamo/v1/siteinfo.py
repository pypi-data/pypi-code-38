"""
This module is for fetching information from dynamo about different sites
"""


from .inventory import _get_inventory


def _small_query(*args):
    """
    This is a wrapper function for opening and closing inventory connection

    :param args: arguments to pass to query
    :returns: Result of the query
    :rtype: list
    """

    mysql_reg = _get_inventory()
    sql = args[0]
    result = mysql_reg.query(sql, *(args[1:]))
    mysql_reg.close()

    return result


def site_list():
    """
    :returns: The list of sites dynamo is storing
    :rtype: list
    """

    return _small_query('SELECT name FROM sites')


_READY = None        # A cached list of ready sites

def ready_sites():
    """
    :returns: Set of sites that are in ready status
    :rtype: set
    """

    global _READY    # pylint: disable=global-statement

    if _READY is None:
        _READY = set(_small_query('SELECT name FROM sites WHERE status = "ready"'))

    return _READY


def get_gfal_location(site):
    """
    :param str site: A site that we want to list with GFAL
    :returns: The host and path needed by the gfal-ls command
    :rtype: str
    """

    return _small_query('SELECT backend FROM sites WHERE name=%s', site)[0]
