# pylint: disable=import-error

"""
Module for interaction with the dynamo inventory
"""

import time
import logging
from datetime import datetime

from dynamo.fileop.rlfsm import RLFSM
from dynamo.dataformat import Dataset
from dynamo.core.executable import inventory


LOG = logging.getLogger(__name__)


def protected_datasets(site):
    """
    :returns: the set of datasets that shouldn't be removed from a given site
    :rtype: set
    """

    acceptable_orphans = set(drobj.dataset.name for drobj in
                             inventory.sites[site].dataset_replicas())

    acceptable_orphans.update(
        dsobj.name for dsobj in inventory.datasets.itervalues() if
        dsobj.status == Dataset.STAT_IGNORED
        )

    rlfsm = RLFSM()

    # Do not delete files being transferred by Dynamo
    acceptable_orphans.update(
        rlfsm.db.query(
            """
            SELECT DISTINCT d.`name` FROM `file_subscriptions` AS u
            INNER JOIN `files` AS f ON f.`id` = u.`file_id`
            INNER JOIN `blocks` AS b ON b.`id` = f.`block_id`
            INNER JOIN `datasets` AS d ON d.`id` = b.`dataset_id`
            INNER JOIN `sites` AS s ON s.`id` = u.`site_id`
            WHERE s.`name` = %s AND u.`delete` = 0
            """,
            site
        )
    )

    rlfsm.db.close()

    return acceptable_orphans


def list_files(site):
    """
    :returns: The dynamo list of files in the inventory for a site
    :rtype: generator
    """

    now = time.time()

    for dataset in inventory.datasets.itervalues():
        for block in dataset.blocks:
            for replica in block.replicas:

                if replica.site.name == site:

                    timestamp = 0 if \
                                replica.is_complete() and \
                                replica.group.id else \
                                now

                    for fileobj in replica.block.files:
                        LOG.debug('File: %s, %s, %s', fileobj.lfn, fileobj.size, timestamp)
                        yield (fileobj.lfn, fileobj.size, datetime.fromtimestamp(timestamp))


def filelist_to_blocklist(site, filelist):
    """
    :param str site: Used to query the inventory
    :param str filelist: Location of list of files
    :returns: tuples of dataset, block, and group
    :rtype: generator
    """

    with open(filelist, 'r') as input_file:
        for line in input_file:
            fileobj = inventory.find_file(line.strip())

            for replica in fileobj.block.replicas:
                if replica.site.name == site:

                    blockobj = fileobj.block

                    dataset = blockobj.dataset.name
                    block = blockobj.name
                    group = replica.group.name or 'Unsubscribed'

                    yield (dataset, block, group)
