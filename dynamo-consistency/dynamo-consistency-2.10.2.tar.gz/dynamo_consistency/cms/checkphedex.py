"""
A module that provides functions to check the comparison results to
the list of files and deletions in PhEDEx.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

import time
import logging

from cmstoolbox.webtools import get_json

from .. import config

LOG = logging.getLogger(__name__)

def deletion_requests(site):
    """
    Get a list of datasets with approved deletion requests at a given site that were created
    within the number of days matching the **IgnoreAge** configuration parameter.
    This request is done via the PhEDEx ``deleterequests`` API.

    :param str site: The site that we want the list of deletion requests for.
    :returns: Datasets that are in deletion requests
    :rtype: set
    """

    created_since = int(
        time.time() - float(config.config_dict().get('IgnoreAge', 0)) * 24 * 3600)

    # Get deletion requests in PhEDEx
    deletion_request = get_json(
        'cmsweb.cern.ch', '/phedex/datasvc/json/prod/deleterequests',
        {'node': site, 'approval': 'approved', 'create_since': created_since},
        use_https=True)

    # PhEDEx APIs are ridiculous
    # Here I get the dataset names of approved deletion requests in a single list
    datasets_for_deletion = set(
        [block['name'].split('#')[0]
         for request in deletion_request['phedex']['request']
         for block in request['data']['dbs']['block']]
        +
        [dataset['name']
         for request in deletion_request['phedex']['request']
         for dataset in request['data']['dbs']['dataset']]
        ) if deletion_request else set()

    return datasets_for_deletion


def get_files(site, dataset):
    """
    Get the list of file replicas at a site for a given dataset.
    This is done via the PhEDEx ``filereplicas`` API.

    :param str site: The name of the site to check
    :param str dataset: The name of the dataset to check
    :returns: A list of files at the site for a given dataset
    :rtype: list
    """

    phedex_response = get_json(
        'cmsweb.cern.ch', '/phedex/datasvc/json/prod/filereplicas',
        {'node': site, 'dataset': dataset},
        use_https=True)

    return [fileinfo['name']
            for block in phedex_response['phedex']['block']
            for fileinfo in block['file']]


def check_datasets(site, orphan_list_file):
    """
    Checks PhEDEx exhaustively to see if a dataset should exist at a site,
    according to PhEDEx, but has files marked as orphans according to our check.
    The number of filereplicas for each dataset is printed to the terminal.
    Datasets that contain any filereplicas are returned by this function.

    :param str site: The name of the site to check
    :param list orphan_list_file: List of LFNs that are listed as orphans at the site
    :returns: The list of number of files and datasets for each dataset that is
              supposed to have at least 1 file at the site.
    :rtype: list of tuples
    """

    datasets = set()

    output = []

    with open(orphan_list_file) as orphans:
        for line in orphans:
            split_name = line.split('/')
            dataset = '/%s/%s-%s/%s' % (split_name[4], split_name[3], split_name[6], split_name[5])

            if dataset not in datasets:
                num_files = len(get_files(site, dataset))

                datasets.add(dataset)

                LOG.debug('%i: %s', num_files, dataset)

                if num_files:
                    output.append((num_files, dataset))

    return output
