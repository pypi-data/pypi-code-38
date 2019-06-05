from pkg_resources import DistributionNotFound, get_distribution


def get_version(package='missinglinkai-resource-manager-docker'):
    try:
        dist = get_distribution(package)
    except DistributionNotFound:
        return None

    return str(dist.version)
