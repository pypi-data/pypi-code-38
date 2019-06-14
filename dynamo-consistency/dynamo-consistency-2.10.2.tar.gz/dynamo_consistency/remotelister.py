"""
Tool to get the files located at a site.

:author: Daniel Abercrombie <dabercro@mit.edu> \n
         Max Goncharov <maxi@mit.edu>
"""


import logging

from . import config
from . import datatypes
from . import create

from .cache import cache_tree
from .backend import get_listers


LOG = logging.getLogger(__name__)


@cache_tree('ListAge', 'remote')
def listing(site, callback=None):
    """
    Get the information for a site, from XRootD or a cache.

    :param str site: The site name
    :param function callback: The callback function to pass to
                              :py:func:`create.create_dirinfo`
    :returns: The site directory listing information
    :rtype: dynamo_consistency.datatypes.DirectoryInfo
    """

    constructor, params = get_listers(site)

    # If the "constructor" is the fully constructed DirectoryInfo, return
    if constructor.__class__ == datatypes.DirectoryInfo:
        return constructor

    config_dict = config.config_dict()

    directories = [
        create.create_dirinfo(
            config_dict['RootPath'], directory, constructor, params, callback)
        for directory in config_dict.get('DirectoryList', [])
        ]

    # Return the DirectoryInfo
    return datatypes.DirectoryInfo(name=config_dict['RootPath'], directories=directories)
