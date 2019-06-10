# pylint: disable=import-error

"""
Defines commands for submitting deletion and transfer requests
"""

import logging


from dynamo.dataformat import Site
from dynamo.fileop.rlfsm import RLFSM
from dynamo.core.executable import inventory


LOG = logging.getLogger(__name__)


def delete(site, files):
    """
    Enters files into the deletion queue for a site
    :param str site: Site to execute deletion
    :param list files: Full LFNs of files or directories to delete
    :returns: Number of files deleted, in case ``files`` is an rvalue or something
    :rtype: int
    """

    rlfsm = RLFSM()
    siteobj = inventory.sites[site]

    for path in files:
        path = path.strip()
        LOG.info('Deleting %s', path)

        rlfsm.desubscribe_file(
            siteobj, inventory.find_file(path))

    rlfsm.db.close()

    return len(files)


def transfer(site, files):
    """
    Requests a transfer for files from other sites
    :param str site: The target site for the transfer
    :param list files: List of file LFNs to transfer
    :returns: Two lists of files.
              The first list is of files that were not on another disk.
              The second list is of files that were also not on tape.
    :rtype: list, list
    """

    rlfsm = RLFSM()
    siteobj = inventory.sites[site]

    no_disk = []
    unrecoverable = []

    for line in files:

        path = line.strip()
        fileobj = inventory.find_file(path)

        ondisk = False
        ontape = False

        for repl in fileobj.block.replicas:
            if repl.site == siteobj:
                continue

            if not repl.has_file(fileobj):
                continue

            if repl.site.storage_type == Site.TYPE_DISK:
                ondisk = True
            elif repl.site.storage_type == Site.TYPE_MSS:
                ontape = True

        if not ondisk:
            no_disk.append(line)
            if not ontape:
                unrecoverable.append(line)

        if ondisk or ontape:
            rlfsm.subscribe_file(siteobj, fileobj)

        LOG.info('Copying %s', path)

    rlfsm.db.close()

    return no_disk, unrecoverable
