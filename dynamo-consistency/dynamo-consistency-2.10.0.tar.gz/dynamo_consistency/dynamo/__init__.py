"""
This sub-module includes all of the interaction with dynamo
"""


import logging

from collections import defaultdict

from .. import opts


LOG = logging.getLogger(__name__)

# This is the old version of connecting to dynamo
if opts.V1:
    LOG.warning('Using v1 of dynamo interface')
    from .v1 import inventory
    from .v1 import registry
    from .v1 import siteinfo

# The new version is designed to run as a script on the dynamo server
else:
    from .v2 import inventory
    from .v2 import siteinfo

    if opts.V1_REPORTING:
        from .v1 import registry
    else:
        from .v2 import registry

def filelist_to_blocklist(site, filelist, blocklist):
    """
    Reads in a list of files, and generates a summary of blocks

    :param str site: Used to query the inventory
    :param str filelist: Location of list of files
    :param str blocklist: Location where to write block report
    """


    # We want to track which blocks missing files are coming from
    track_missing_blocks = defaultdict(
        lambda: {'errors': 0,
                 'blocks': defaultdict(lambda: {'group': '',
                                                'errors': 0}
                                      )
                })


    for dataset, block, group in inventory.filelist_to_blocklist(site, filelist):

        track_missing_blocks[dataset]['errors'] += 1
        track_missing_blocks[dataset]['blocks'][block]['errors'] += 1
        track_missing_blocks[dataset]['blocks'][block]['group'] = group


    # Output file with the missing datasets
    with open(blocklist, 'w') as output_file:
        for dataset, vals in \
                sorted(track_missing_blocks.iteritems(),
                       key=lambda x: x[1]['errors'],
                       reverse=True):

            for block_name, block in sorted(vals['blocks'].iteritems()):
                output_file.write('%10i    %-17s  %s#%s\n' % \
                                      (block['errors'], block['group'],
                                       dataset, block_name))
