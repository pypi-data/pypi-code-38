"""
Holds the main function for running the consistency check
"""

import os
import json
import logging
import shutil
import time
import datetime


from . import opts
from . import config
from . import inventorylister
from . import remotelister
from . import datatypes
from . import summary
from . import filters
from . import history
from .backend import registry
from .backend import inventory
from .backend import filelist_to_blocklist
from .backend import deletion_requests
from .backend import DatasetFilter
from .emptyremover import EmptyRemover
from .logsetup import match_logs


LOG = logging.getLogger(__name__)


def make_filters(site):
    """
    Creates filters proper for running environment and options

    :param str site: Site to get activity at
    :returns: Three :py:class:`filters.Filter` objects that can be used
              to check orphans, missing files, and ignored directories respectively
    :rtype: :py:class:`filters.Filter`, :py:class:`filters.Filter`,
            :py:class:`filters.PatternFilter`
    """

    ignore_list = config.config_dict().get('IgnoreDirectories', [])

    pattern_filter = filters.PatternFilter(ignore_list)

    # First, datasets in the deletions queue can be missing
    acceptable_missing = deletion_requests(site)
    # Orphan files cannot belong to any dataset that should be at the site
    acceptable_orphans = inventory.protected_datasets(site)
    # Orphan files may be a result of deletion requests
    acceptable_orphans.update(acceptable_missing)

    make = lambda accept: filters.Filters(DatasetFilter(accept).protected,
                                          pattern_filter.protected)

    # If no orphans are to be listed, mark everything for keeping
    no_orphans = opts.NOORPHAN or (not config.config_dict().get('DeleteOrphans', True))

    return (filters.FullFilter() if no_orphans else make(acceptable_orphans),
            DatasetFilter(acceptable_missing),
            pattern_filter)


def extras(site):
    """
    Runs a bunch of functions after the main consistency check,
    depending on the presence of certain arguments and configuration

    :param str site: For use to pass to extras
    :returns: Dictionary with interesting results. Keys include the following:

              - ``"unmerged"`` - A tuple listing unmerged files removed and unmerged logs

    :rtype: dict
    """

    output = {}

    if opts.UNMERGED and site in config.config_dict().get('Unmerged', []):
        # This is a really ugly thing, so we hide it here
        from .cms import unmerged

        match_logs(LOG, [unmerged.LOG, unmerged.listdeletable.LOG])

        output['unmerged'] = unmerged.clean_unmerged(site)

    work = config.vardir('work')

    # Convert missing files to blocks
    filelist_to_blocklist(site,
                          os.path.join(work, '%s_compare_missing.txt' % site),
                          os.path.join(work, '%s_missing_datasets.txt' % site))

    return output


def report_files(inv, remote, missing, orphans, prev_set=None):
    """
    Reports files to the history database.
    If ``prev_set`` is given, only missing files that
    also appear in this set will be invalidated.

    :param dynamo_consistency.datatypes.DirectoryInfo inv: The inventory listing
    :param dynamo_consistency.datatypes.DirectoryInfo remote: The remote listing
    :param list missing: Missing files
    :param list orphans: Orphan files
    :param set prev_set: Set of files that were missing in the previous run
    """
    history.report_missing([(name, inv.get_file(name)) for name in missing if
                            prev_set is None or name in prev_set])
    history.report_orphan([(name, remote.get_file(name)) for name in orphans])


# Need to make this smaller
def compare_with_inventory(site):    # pylint: disable=too-many-locals
    """
    Gets the listing from the dynamo database, and remote XRootD listings of a given site.
    The differences are compared to deletion queues and other things.

    :param str site: The site to run the check over
    :returns: Start time of the running and
              a dictionary of parameters to report to the summary webpage.
              See :py:func:`summary.update_summary` parameters for returned keys.
    :rtype: float, dict
    """

    start = time.time()

    # Filter out missing files that were not missing previously
    config_dict = config.config_dict()

    prev_missing = os.path.join(summary.webdir(), '%s_compare_missing.txt' % site)
    prev_set = set()

    if os.path.exists(prev_missing):
        with open(prev_missing, 'r') as prev_file:
            for line in prev_file:
                prev_set.add(line.strip())

        if int(config_dict.get('SaveCache')):
            prev_new_name = '%s.%s' % (prev_missing,
                                       datetime.datetime.fromtimestamp(
                                           os.stat(prev_missing).st_mtime).strftime('%y%m%d')
                                      )
        else:
            prev_new_name = os.path.basename(prev_missing)

        shutil.move(prev_missing,
                    os.path.join(config.vardir('web_bak'),
                                 prev_new_name)
                   )
    else:
        prev_set = None

    inv_tree = inventorylister.listing(site)

    check_orphans, check_missing, ignored_patterns = make_filters(site)

    # Reset the DirectoryList for the XRootDLister to run on
    config.DIRECTORYLIST = [directory.name for directory in inv_tree.directories]
    remover = EmptyRemover(site, ignored_patterns.protected)
    site_tree = remotelister.listing(site, remover)

    work = config.vardir('work')

    # Do the comparison
    missing, m_size, orphan, o_size = datatypes.compare(
        inv_tree, site_tree, os.path.join(work, '%s_compare' % site),
        orphan_check=check_orphans.protected,
        missing_check=check_missing.protected)

    report_files(inv_tree, site_tree, missing, orphan, prev_set)

    LOG.info('Missing size: %i, Orphan size: %i', m_size, o_size)

    # Determine if files should be entered into the registry

    many_missing = len(missing) > int(config_dict['MaxMissing'])
    many_orphans = len(orphan) > int(config_dict['MaxOrphan'])

    # Track files with no sources
    no_source_files = []
    unrecoverable = []

    if not many_missing and not many_orphans:
        registry.delete(site, orphan)

        # Don't report any until it shows up twice, or if this is first listing
        no_source_files, unrecoverable = registry.transfer(
            site, [f for f in missing if prev_set is None or f in prev_set])

    else:

        if many_missing:
            LOG.error('Too many missing files: %i, you should investigate.', len(missing))

        if many_orphans:
            LOG.error('Too many orphan files: %i out of %i, you should investigate.',
                      len(orphan), site_tree.get_num_files())


    with open(os.path.join(work, '%s_missing_nosite.txt' % site),
              'w') as nosite:
        for line in no_source_files:
            nosite.write(line + '\n')

    with open(os.path.join(work, '%s_unrecoverable.txt' % site),
              'w') as output_file:
        output_file.write('\n'.join(unrecoverable))

    if summary.do_update():

        # Make a JSON file reporting storage usage
        if site_tree and site_tree.get_num_files():
            storage = {
                'storeageservice': {
                    'storageshares': [{
                        'numberoffiles': node.get_num_files(),
                        'path': [os.path.normpath(os.path.join(site_tree.name, subdir))],
                        'timestamp': str(int(time.time())),
                        'totalsize': 0,
                        'usedsize': node.get_directory_size()
                        } for node, subdir in [(site_tree.get_node(path), path) for path in
                                               [''] + [d.name for d in site_tree.directories]]
                                      if node.get_num_files()]
                    }
                }

            with open(os.path.join(summary.webdir(), '%s_storage.json' % site), 'w') \
                    as storage_file:
                json.dump(storage, storage_file)


        unlisted = site_tree.get_unlisted()

        return start, {
            'numfiles': site_tree.get_num_files(),
            'numnodes': remover.get_removed_count() + site_tree.count_nodes(),
            'numempty': remover.get_removed_count(),
            'nummissing': len(missing),
            'missingsize': m_size,
            'numorphan': len(orphan),
            'orphansize': o_size,
            'numnosource': len(no_source_files),
            'numunrecoverable': len(unrecoverable),
            'numunlisted': len(unlisted),
            'numbadunlisted': len([d for d in unlisted
                                   if True not in
                                   [i in d for i in config_dict['IgnoreDirectories']]]),
            }

    return start, {}

def main(site):
    """
    Runs comparison, and extras based on command line.
    Updates the summary table for normal runs.

    :param str site: Site to run over
    """

    history.start_run()

    start, report = compare_with_inventory(site)

    extras_results = extras(site)

    unmerged, unmergedlogs = extras_results.get('unmerged', (0, 0))

    # If one of these is set by hand, then probably reloading cache,
    # so don't update the summary table
    if summary.do_update():

        summary.update_summary(
            site=site,
            duration=time.time() - start,
            numunmerged=unmerged,
            numlogs=unmergedlogs,
            **report)

        summary.move_local_files(site)
        summary.update_config()

    history.finish_run()
