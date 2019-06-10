"""
This module gets the information from the inventory about a site's contents

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

import time
import logging

from . import datatypes
from . import config

from .cache import cache_tree
from .backend import inventory


LOG = logging.getLogger(__name__)


def filter_files(site, pathstrip):
    """
    Gets the files from the inventory and filters them through
    the configuration's **DirectoryList**

    :param str site: The site to get the files from
    :param int pathstrip: The length of the root node's name that
                          is stripped from the directory name for filtering
    :returns: Tuples for adding to
              :py:func:`dynamo_consistency.datatypes.DirectoryInfo.add_file_list`
    :rtype: generator
    """

    dirlist = sorted(config.config_dict()['DirectoryList'])

    dirs_to_look = iter(dirlist)

    last_file = ''
    look_dir = ''

    for row in inventory.list_files(site):

        # If the list is not sorted, we have to start the filter from the beginning
        if row[0] < last_file:
            dirs_to_look = iter(dirlist)
        elif dirs_to_look is None:
            continue

        name, size = row[0:2]
        timestamp = time.mktime(row[2].timetuple()) if len(row) == 3 else 0

        current_directory = name[pathstrip:].split('/')[1]
        try:
            while look_dir < current_directory:
                look_dir = next(dirs_to_look)
        except StopIteration:
            dirs_to_look = None
            continue

        if current_directory == look_dir:
            yield (name, size, timestamp)


@cache_tree('InventoryAge', 'inventory')
def listing(site):
    """
    Get the list of files from the inventory.

    :param str site: The name of the site to load
    :returns: The file replicas that are supposed to be at a site
    :rtype: dynamo_consistency.datatypes.DirectoryInfo
    """

    treeroot = config.config_dict()['RootPath']
    tree = datatypes.DirectoryInfo(treeroot)

    tree.add_file_list(filter_files(site, len(treeroot)))

    LOG.info('Finished building inventory tree')

    return tree
