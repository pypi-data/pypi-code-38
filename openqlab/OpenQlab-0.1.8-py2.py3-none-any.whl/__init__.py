from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'

__all__ = ['analysis', 'io', 'plots', 'conversion']

try:
    from .io.data_container import DataContainer
except ImportError:
    print('Unable to import DataContainer')
