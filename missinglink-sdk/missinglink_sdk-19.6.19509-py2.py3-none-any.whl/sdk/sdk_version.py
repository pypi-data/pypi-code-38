# -*- coding: utf-8 -*-

import os


def get_dist():
    from pkg_resources import get_distribution, DistributionNotFound

    dist = get_distribution('missinglink-kernel')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(dist.location)
    here = os.path.normcase(__file__)

    if not here.startswith(os.path.join(dist_loc, 'missinglink')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound

    return dist


def get_version():
    from pkg_resources import DistributionNotFound

    try:
        dist = get_dist()
    except DistributionNotFound:
        return None

    return dist.version
