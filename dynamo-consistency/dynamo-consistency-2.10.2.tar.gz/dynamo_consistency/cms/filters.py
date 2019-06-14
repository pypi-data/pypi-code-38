"""
This module defines any filters that are used specifically for CMS.
"""

import logging


LOG = logging.getLogger(__name__)


class DatasetFilter(object):
    """
    Filter to check if files are in the CMS-style datasets

    :param set datasets: Set (or other collection) of datasets using CMS notation
                         that we want to identify files as part of
    """

    def __init__(self, datasets):
        self._datasets = datasets

    def protected(self, file_name):
        """
        Returns whether the file is in a stored dataset.
        If the file name is not structured in a way to get the dataset out,
        then this function chooses to filter it out.

        :param str file_name: Full LFN of file
        :returns: If file belongs to a dataset that is stored
        :rtype: bool
        """

        LOG.debug('Checking file_name: %s', file_name)

        split_name = file_name.split('/')

        try:
            return '/%s/%s-%s/%s' % (split_name[4], split_name[3],
                                     split_name[6], split_name[5]) in self._datasets
        except IndexError:
            LOG.warning('Strange file name: %s', file_name)
            return True
