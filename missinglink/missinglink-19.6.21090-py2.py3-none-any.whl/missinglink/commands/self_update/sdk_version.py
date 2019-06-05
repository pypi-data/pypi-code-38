# -*- coding: utf-8 -*-
def get_dist(package):
    from pkg_resources import get_distribution

    return get_distribution(package)


def get_keywords(package):
    from pkg_resources import DistributionNotFound

    try:
        dist = get_dist(package)
    except DistributionNotFound:
        return None

    parsed_pkg_info = getattr(dist, '_parsed_pkg_info', None)

    if parsed_pkg_info is None:
        return None

    return parsed_pkg_info.get('Keywords')


def get_version(package):
    from pkg_resources import DistributionNotFound

    try:
        dist = get_dist(package)
    except DistributionNotFound:
        return None

    return str(dist.version)
