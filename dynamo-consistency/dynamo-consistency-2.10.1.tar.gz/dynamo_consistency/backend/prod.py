# pylint: disable=unused-import

"""
This module imports the commands from dynamo and CMS.
Other modules should import everything from here.
"""

import os
import sys
import json
import time
import logging

from .. import opts
from .. import config

# Required abstractions from dynamo
from ..dynamo import registry
from ..dynamo import siteinfo
from ..dynamo import inventory
from ..dynamo import filelist_to_blocklist

# Get the listers, taking GFAL from appropriate siteinfo
from . import listers
from .listers import get_listers

LOG = logging.getLogger(__name__)

# Getting datasets for filtering
# protected_datasets actually in inventory module (not file)
protected_datasets = inventory.protected_datasets  # pylint: disable=invalid-name

listers.GFAL_LOCATION = siteinfo.get_gfal_location

# Check if site is ready, according to dynamo
_READY = lambda site: site in siteinfo.ready_sites()

if opts.CMS:

    from cmstoolbox.samstatus import is_sam_good
    from ..cms.checkphedex import deletion_requests

    from ..cms.filters import DatasetFilter

    def check_site(site):
        """Checks SAM tests and dynamo"""
        sam = is_sam_good(site) or opts.NOSAM
        ready = _READY(site)
        LOG.debug('Site: %s, SAM: %s, Ready: %s', site, sam, ready)
        return sam and ready

else:

    def check_site(site):
        """Should return if the site is ready to run over or not"""
        return _READY(site)

    def deletion_requests(_):
        """Should return the set of deletion requests that may still be pending"""
        return set()

    class DatasetFilter(object):
        """
        .. warning::

           Needs implemented properly for vanilla dyanmo

        """
        def __init__(self, _):
            pass

        @staticmethod
        def protected(_):
            """Needs a fast way to translate from name to dataset"""
            return False    # This protects nothing
