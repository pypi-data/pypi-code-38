# pylint: disable=missing-docstring
# We don't really need the docstring for the functions inside the decorator

import os
import time
import datetime
import logging

from functools import wraps
from . import config
from . import datatypes


LOG = logging.getLogger(__name__)


def cache_tree(config_age, location_suffix):
    """
    A decorator for caching pickle files based on the configuration file.
    It is currently set up to decorate a function that has a single parameter ``site``.

    The returned function also can be passed keyword arguments to override the
    ``location_suffix`` argument.
    This is done with the ``cache`` argument to the function.

    :param str config_age: The key from the config file to read the max age from
    :param str location_suffix: The ending of the main part of the file name
                                where the cached file is saved.
    :returns: A function that uses the caching configuration
    :rtype: func
    """

    def func_decorator(func):

        @wraps(func)
        def do_function(site, callback=None, **kwargs):

            config_dict = config.config_dict()

            # Make cache directory if it doesn't exist first
            cache_dir = os.path.join(config_dict['VarLocation'], 'cache', site)
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)

            # Overwrite location_suffix if that's desired
            cache_location = os.path.join(
                cache_dir, '%s.pkl' % kwargs.get('cache', location_suffix))

            LOG.info('Checking for cache at %s', cache_location)

            if not os.path.exists(cache_location) or \
                    (time.time() - os.stat(cache_location).st_mtime) > \
                    float(config_dict.get(config_age, 0)) * 24 * 3600:

                if int(config_dict.get('SaveCache')) and os.path.exists(cache_location):
                    os.rename(cache_location,
                              '%s.%s' % (cache_location,
                                         datetime.datetime.fromtimestamp(
                                             os.stat(cache_location).st_mtime).strftime('%y%m%d')
                                        )
                             )

                LOG.info('Cache is no good, getting new tree')
                if callback is None:
                    tree = func(site)
                else:
                    tree = func(site, callback)
                LOG.info('Making hash')
                tree.setup_hash()
                LOG.info('Saving tree at %s', cache_location)
                tree.save(cache_location)

            else:

                LOG.info('Loading tree from cache')
                tree = datatypes.get_info(cache_location)

            return tree

        return do_function

    return func_decorator
