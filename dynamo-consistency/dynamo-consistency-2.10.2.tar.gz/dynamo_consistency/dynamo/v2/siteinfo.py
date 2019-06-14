# pylint: disable=import-error

"""
This module is for fetching information from dynamo about different sites
"""


from dynamo.dataformat import Site
from dynamo.core.executable import inventory


def site_list():
    """
    :returns: The list of sites dynamo is storing
    :rtype: list
    """

    return inventory.sites.keys()


def ready_sites():
    """
    :returns: Set of sites that are in ready status
    :rtype: set
    """

    return set([site.name for site in inventory.sites.itervalues() if
                site.status == Site.STAT_READY])


def get_gfal_location(site):
    """
    :param str site: A site that we want to list with GFAL
    :returns: The host and path needed by the gfal-ls command
    :rtype: str
    """

    fake = '/store/mc'
    return inventory.sites[site].to_pfn(fake, 'gfal2')[:-1 * len(fake)]
