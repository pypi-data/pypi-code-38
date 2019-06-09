"""
Defines commands for submitting deletion and transfer requests
"""

import os
import logging

# Problem on Travis
import MySQLdb # pylint: disable=import-error

from ... import opts
from ... import config
from ... import summary

from .mysql import MySQL

from .inventory import _get_inventory


LOG = logging.getLogger(__name__)


def _get_registry(is_debugged):
    """
    The connection returned by this must be closed by the caller

    :returns: A connection to the registry database.
    :rtype: :py:class:`MySQL`
    """
    # Super quick bad hack to point to the right thing if inside server
    if (os.environ.get('DYNAMO_SPOOL') or os.environ['USER'] == 'dynamo') \
            and opts.CMS and is_debugged:
        return MySQL(config_file=opts.CNF,
                     db='dynamoregister', config_group='mysql-dynamo')

    # This is also really bad. Only works at MIT.
    LOG.warning('Connecting to test database')

    return MySQL(**(
        config.config_dict().get('DBConfig', {}).get(
            'Registry',
            { # Default registry config
                'config_file': opts.CNF,
                'db': 'dynamoregister',
                'config_group': 'mysql-register-test'
            }
        )))


def delete(site, files):
    """
    Enters files into the deletion queue for a site

    :param str site: Site to execute deletion
    :param list files: Full LFNs of files or directories to delete
    :returns: Number of files deleted, in case ``files`` is an rvalue or something
    :rtype: int
    """

    try:
        reg_sql = _get_registry(summary.is_debugged(site))
    except MySQLdb.OperationalError as exce:
        LOG.error('OperationalError! not actually deleting files')
        LOG.error(exce)
        return len(files)

    for path in files:
        path = path.strip()
        LOG.info('Deleting %s', path)
        reg_sql.query(
            """
            INSERT IGNORE INTO `deletion_queue`
            (`file`, `site`, `status`) VALUES
            (%s, %s, 'new')
            """, path, site)
    reg_sql.close()

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

    no_disk = []
    unrecoverable = []

    inv_sql = _get_inventory()
    reg_sql = _get_registry(summary.is_debugged(site))

    # Setup a query for sites, with added condition at the end
    site_query = """
                 SELECT sites.name FROM sites
                 INNER JOIN block_replicas ON sites.id = block_replicas.site_id
                 INNER JOIN files ON block_replicas.block_id = files.block_id
                 WHERE files.name = %s AND sites.name != %s
                 AND sites.status = 'ready'
                 AND block_replicas.is_complete = 1
                 AND group_id != 0
                 {0}
                 """

    for line in files:

        # Get sites that are not tape
        sites = inv_sql.query(
            site_query.format('AND sites.storage_type != "mss"'),
            line, site)

        if not sites:
            no_disk.append(line)
            sites = inv_sql.query(
                site_query.format('AND sites.storage_type = "mss"'),
                line, site)
            # If still no sites, we are not getting this file back
            if not sites:
                unrecoverable.append(line)

        # Don't add transfers if too many missing files
        for location in sites:
            reg_sql.query(
                """
                INSERT IGNORE INTO `transfer_queue`
                (`file`, `site_from`, `site_to`, `status`, `reqid`)
                VALUES (%s, %s, %s, 'new', 0)
                """,
                line, location, site)

            LOG.info('Copying %s from %s', line, location)

    reg_sql.close()
    inv_sql.close()

    return no_disk, unrecoverable
