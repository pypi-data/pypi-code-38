"""
Module for interaction with the dynamo inventory
"""

import logging

from .mysql import MySQL


LOG = logging.getLogger(__name__)


def _get_inventory():
    """
    The connection returned by this must be closed by the caller

    :returns: A connection to the inventory database.
    :rtype: :py:class:`MySQL`
    """
    return MySQL(config_file='/etc/my.cnf', db='dynamo', config_group='mysql-dynamo')


def protected_datasets(site):
    """
    :returns: the set of datasets that shouldn't be removed from a given site
    :rtype: set
    """
    inv_sql = _get_inventory()
    acceptable_orphans = set(
        inv_sql.query(
            """
            SELECT datasets.name FROM sites
            INNER JOIN dataset_replicas ON dataset_replicas.site_id=sites.id
            INNER JOIN datasets ON dataset_replicas.dataset_id=datasets.id
            WHERE sites.name=%s
            """,
            site)
        )

    acceptable_orphans.update(
        inv_sql.query('SELECT name FROM datasets WHERE status=%s', 'IGNORED')
        )

    # Do not delete files being transferred by Dynamo
    acceptable_orphans.update(
        inv_sql.query(
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

    return acceptable_orphans


def list_files(site):
    """
    :returns: The dynamo list of files in the inventory for a site
    :rtype: generator
    """

    inv_sql = _get_inventory()
    curs = inv_sql._connection.cursor()    # pylint: disable=protected-access

    LOG.info('About to make MySQL query for files at %s', site)

    for query in [
            """
            SELECT files.name, files.size
            FROM block_replicas
            INNER JOIN sites ON block_replicas.site_id = sites.id
            INNER JOIN files ON block_replicas.block_id = files.block_id
            WHERE block_replicas.is_complete = 1 AND sites.name = %s
            AND group_id != 0
            ORDER BY files.name ASC
            """,
            """
            SELECT files.name, files.size, NOW()
            FROM block_replicas
            INNER JOIN sites ON block_replicas.site_id = sites.id
            INNER JOIN files ON block_replicas.block_id = files.block_id
            WHERE (block_replicas.is_complete = 0 OR group_id = 0) AND sites.name = %s
            ORDER BY files.name ASC
            """]:


        curs.execute(query, (site,))

        row = curs.fetchone()

        while row:
            yield row
            row = curs.fetchone()


def filelist_to_blocklist(site, filelist):
    """
    :param str site: Used to query the inventory
    :param str filelist: Location of list of files
    :returns: tuples of dataset, block, and group
    :rtype: generator
    """

    blocks_query = """
                   SELECT blocks.name, IFNULL(groups.name, 'Unsubscribed') FROM blocks
                   INNER JOIN files ON files.block_id = blocks.id
                   INNER JOIN block_replicas ON block_replicas.block_id = files.block_id
                   INNER JOIN sites ON block_replicas.site_id = sites.id
                   LEFT JOIN groups ON block_replicas.group_id = groups.id
                   WHERE files.name = %s AND sites.name = %s
                   """

    inv_sql = _get_inventory()

    with open(filelist, 'r') as input_file:
        for line in input_file:
            ### This is CMS specific. Move into ...cms ###
            split_name = line.split('/')
            dataset = '/%s/%s-%s/%s' % (split_name[4], split_name[3], split_name[6], split_name[5])

            output = inv_sql.query(blocks_query, line.strip(), site)

            if not output:
                LOG.error('The following SQL statement failed: %s',
                          blocks_query % (line.strip(), site))
                LOG.error('Most likely cause is dynamo update between the listing and now')
                continue

            block, group = output[0]

            yield (dataset, block, group)

    inv_sql.close()
