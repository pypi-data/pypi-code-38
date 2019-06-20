from .discoverers import DiscovererList


__version__ = '2.5.0'
__all__ = [
    'discovery',
    'get_version'
]


default_app_config = 'oembed.apps.OembedAppConfig'
discovery = DiscovererList()


def get_version():
    return __version__
