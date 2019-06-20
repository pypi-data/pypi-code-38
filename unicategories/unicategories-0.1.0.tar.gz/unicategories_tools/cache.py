
import io
import os
import os.path
import pickle
import unicodedata
import warnings

import unicategories_tools as tools

try:
    from importlib.resources import open_binary as open_binary_resource
except ImportError:  # pragma: no cover
    from pkg_resources import resource_stream as open_binary_resource


cache_formats = ('0.0.6', 'v1')
cache_version = unicodedata.unidata_version


def load_from_package(package, resource):
    '''
    Try to load category ranges from module.

    :returns: category ranges dict or None
    :rtype: None or dict of RangeGroup
    '''
    try:
        with open_binary_resource(package, resource) as f:
            version, format, data = pickle.load(f)
        if version == cache_version and format in cache_formats:
            return data
        warnings.warn(
            'Unicode unicategories database is outdated. '
            'Please reinstall unicategories module to regenerate it.'
            if version < cache_version else
            'Incompatible unicategories database. '
            'Please reinstall unicategories module to regenerate it.'
            )
    except (ValueError, EOFError):
        warnings.warn(
            'Incompatible unicategories database. '
            'Please reinstall unicategories module to regenerate it.'
            )
    except IOError:
        pass


def load_from_cache(path=None):
    '''
    Try to load category ranges from userlevel cache file.

    :param path: path to userlevel cache file
    :type path: str
    :returns: category ranges dict or None
    :rtype: None or dict of RangeGroup
    '''
    if not path:
        return None
    try:
        with io.open(path, 'rb') as f:
            version, format, data = pickle.load(f)
        if version == cache_version and format in cache_formats:
            return data
    except (IOError, ValueError, EOFError):
        pass


def generate_and_cache(path=None):
    '''
    Generate category ranges and save to userlevel cache file.

    :param path: path to userlevel cache file
    :type path: str
    :returns: category ranges dict
    :rtype: dict of RangeGroup
    '''
    data = tools.generate()
    if not path:
        return data
    try:
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with io.open(path, 'wb') as f:
            pickle.dump((cache_version, cache_formats[-1], data), f)
    except (IOError, ValueError) as e:
        warnings.warn('Unable to write cache file %r: %r' % (path, e))
    return data
