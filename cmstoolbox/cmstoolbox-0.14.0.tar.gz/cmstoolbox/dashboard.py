"""
A module to gather and hold information from the dashboard.

:author: Jean-Roch Vlimant <jean-roch.vlimant@cern.ch>
"""

import os
import copy
import time
import json
import random
import re
import datetime
import logging

from .webtools import get_json


def get_node_usage(url, node):
    """
    Get the disk function useage at a given site.

    .. Note::

       This function only works on systems that have the environment variable
       ``X509_USER_PROXY`` defined.
       Without this function, the cached labels that are formed like ``<site>_usage``
       cannot be refreshed.

    :param str url: is the URL of the reporting service
    :param str node: is the site name to check
    :returns: The disk usage at the site in TB, or None if node info is not found
    :rtype: int
    """

    result = get_json(url, '/phedex/datasvc/json/prod/nodeusage',
                      params={'node': node}, use_cert=True)

    usage = 0

    for node_ in result['phedex']['node']:
        usage = max(
            sum([node_[key] for key in node_.keys() if key.endswith('_node_bytes')]),
            usage
            )

    # in TB
    return int(usage / (1024. ** 4)) or None


def default_expiration():
    """
    :returns: A slightly varying time between 20-30 minutes for the cache duration
    :rtype: float
    """
    return 20 * 60 + random.random() * 10 * 60

def load_json(url, key=''):
    """
    :param str url: is a URL that points to a JSON file containing useful information
    :param str key: is a key of the JSON file to return.
                    If left blank, the entire JSON file is returned
    :returns: a function that downloads a JSON file through curl from the URL.
              This function has no parameters itself so that the
              :py:func:`DocCache.get` function can figure things out on its own.
    :rtype: function
    """
    curl_call = 'curl -s --retry 5 "{0}"'.format(url)

    if key:
        return lambda: load_json(url)()[key]
    return lambda: json.loads(os.popen(curl_call).read())

def make_cache_entry(getter, default, description='no description'):
    """
    :param function getter: is a function with no parameters that obtains the
                            information to store in the cache.
    :param default: the default value to fill the cached data if the information
                    cannot be obtained.
    :type default: str, list, or dict
    :param str description: is the description of the member of the cache
    :returns: a cache entry using the given getter function and default cache value
    :rtype: dict
    """
    return {
        'data': None,
        'timestamp': time.mktime(time.gmtime()),
        'expiration': default_expiration(),
        'getter': getter,
        'cachefile': None,
        'default': default,
        'description': description
        }



class DocCache(object):
    """
    This class gathers various information, mostly from the dashboard when it's requested.
    The information is cached with slightly random lifetimes to allow requests to be staggered.
    All of the information is obtained through system curl commands.
    """

    def __init__(self):
        """Initializes the DocCache without parameters."""
        phedex_url = os.getenv('UNIFIED_PHEDEX', 'cmsweb.cern.ch')
        self.cache = {}

        # Get some columns from the dashboard
        columns = {
            '106': '',
            '107': '',
            '108': '',
            '109': '',
            '136': '',
            '158': '',
            '159': '',
            '160': '',
            '237': 'The Site Readiness'
            }
        for col, desc in columns.items():
            self.cache['ssb_{0}'.format(col)] = make_cache_entry(
                load_json('http://dashb-ssb.cern.ch'
                          '/dashboard/request.py/getplotdata'
                          '?columnid={0}&batch=1&lastdata=1'.format(col),
                          'csvdata'),
                [],
                desc or 'column %s in the dashboard' % col
                )

        sites = [
            'T1_DE_KIT_MSS', 'T1_US_FNAL_MSS', 'T1_ES_PIC_MSS', 'T1_UK_RAL_MSS',
            'T1_IT_CNAF_MSS', 'T1_FR_CCIN2P3_MSS', 'T1_RU_JINR_MSS', 'T0_CH_CERN_MSS'
            ]

        def node_wrapper(site):
            """
            A wrapper to return a lambda that will not change with the reference over a loop.
            Placing the returned lambda into the loop that follows will lead to the referenced
            site changing over each iteration.

            :param str site: is the site to make the function for
            :returns: a function that takes no arguments
            :rtype: function
            """
            return lambda: get_node_usage(phedex_url, site)

        for site in sites:
            self.cache['{0}_usage'.format(site)] = make_cache_entry(
                node_wrapper(site), '', 'Node usage for %s' % site
                )

        self.cache['mss_usage'] = make_cache_entry(
            load_json('http://cmsmonitoring.web.cern.ch'
                      '/cmsmonitoring/StorageOverview/latest/StorageOverview.json'),
            {}
            )

        self.cache['hlt_cloud'] = make_cache_entry(
            load_json('http://137.138.184.204/cache-manager/images/cloudStatus.json'),
            {}
            )

        self.cache['gwmsmon_totals'] = make_cache_entry(
            load_json('http://cms-gwmsmon.cern.ch/poolview/json/totals'),
            {}
            )

        self.cache['mcore_ready'] = make_cache_entry(
            load_json(
                'http://cmsgwms-frontend-global.cern.ch/vofrontend/stage/mcore_siteinfo.json'
                ),
            {}
            )

        self.cache['gwmsmon_prod_site_summary'] = make_cache_entry(
            load_json('http://cms-gwmsmon.cern.ch/prodview/json/site_summary'),
            {}
            )

        self.cache['gwmsmon_site_summary'] = make_cache_entry(
            load_json('http://cms-gwmsmon.cern.ch/totalview/json/site_summary'),
            {}
            )

        self.cache['detox_sites'] = make_cache_entry(
            lambda: os.popen(
                'curl --retry 5 -s '
                'http://t3serv001.mit.edu/~cmsprod/IntelROCCS/Detox/SitesInfo.txt'
                ).read().split('\n'),
            ''
            )

        # create the cache files from the labels
        for src in self.cache:
            self.cache[src]['cachefile'] = os.path.join('/tmp/', src + '.cache.json')

    def get(self, label, fresh=False):
        """
        This is the function that should be used to access data from various monitors of CMS.
        The :py:class:`DocCache` class stores a cache, for the various information which is
        only filled if requested and updates every 20 to 30 minutes.
        The times are staggered to avoid making all of the calls for information at the same time.

        .. todo::

           Create descriptions for all of the members of the cache.

        :param str label: dictionary key of cache for the information desired.
                          The list of valid labels and their description.

%s

        :param bool fresh: forces the cache to be refreshed if true.
                           Otherwise, the cache timestamp is checked.
        :returns: the values of the given cache if a correct label is given,
                  otherwise returns None.
                  The cache is returned as a dictionary with the following keys.

                  - **data** - is the data for a given cache.
                    These have different forms of being either a list, a dict, or a str.
                  - **timestamp** - is the time that the cache was last downloaded
                    or when the object was created.
                  - **expiration** - is the time in seconds that the entry stays until
                    it is redownloaded. It is a random time between 20 to 30 minutes.
                  - **getter** - is a function with zero parameters that will download
                    and return the data corresponding to this column
                  - **cachefile** - is the location of a local file where the cache is saved.
                  - **default** - is the default value of the cache.
                    This should be an empty variable of the appropriate type.
                  - **description** - is the description of the cache member.
                    This is used to generate the documentation for the label parameter.

        :rtype: dict or None
        """

        now = time.mktime(time.gmtime())

        if  label not in self.cache:
            site_status_by_date = re.match(r'ssb_237_(?P<day>\d\d)(?P<month>\d\d)(?P<year>\d\d)'
                                           , label)
            date = datetime.date(int('20'+site_status_by_date.group('year')),
                                 int(site_status_by_date.group('month')),
                                 int(site_status_by_date.group('day')))
            plusoneday = datetime.timedelta(days=1)
            frm_date = date-plusoneday
            to_date = date+plusoneday
            if site_status_by_date:
                self.cache[label] = make_cache_entry(
                    load_json('http://dashb-ssb.cern.ch'
                              '/dashboard/request.py/getplotdata'
                              '?columnid=237&batch=1&site=T0_CH_CERN'
                              '&sites=all&clouds=all&time=custom'
                              '&dateFrom={0:%Y-%m-%d}'
                              '&dateTo={1:%Y-%m-%d}'.format(frm_date, to_date), 'csvdata'),
                    [],
                    'site readiness column for {0}'.format(date)
                    )
                self.cache[label]['cachefile'] = os.path.join('/tmp/', label + '.cache.json')


        if label in self.cache:
            try:
                cache = self.cache[label]

                def update_cache():
                    """perform update operations for the cache."""
                    cache['data'] = cache['getter']()
                    cache['timestamp'] = now
                    with open(cache['cachefile'], 'w') as cachefile:
                        cachefile.write(
                            json.dumps(
                                {
                                    'data': cache['data'],
                                    'timestamp': cache['timestamp']
                                    },
                                indent=2
                                )
                            )

                if not cache['data']:
                    # check the file version
                    if os.path.isfile(cache['cachefile']):
                        logging.info("load %s from file %s", label, cache['cachefile'])
                        with open(cache['cachefile'], 'r') as cachefile:
                            f_cache = json.load(cachefile)
                        cache['data'] = f_cache['data']
                        cache['timestamp'] = f_cache['timestamp']
                    else:
                        logging.info("no file cache for %s getting fresh", label)
                        update_cache()

                # check the time stamp
                if cache['expiration'] + cache['timestamp'] < now or fresh:
                    logging.info("getting fresh %s", label)
                    update_cache()

                return cache['data']

            except Exception as error:
                logging.error("failed to get %s", label)
                logging.error(str(error))
                return copy.deepcopy(cache['default'])

        return None


GLOBAL_CACHE = DocCache()
"""A global instance of the :py:class:`DocCache` that should be used."""

# Automatically generate documentation from the descriptions of the cache members
DOC_LIST = '\n'.join(
    [' ' * 26 + '- **' + c_key + '** - ' + GLOBAL_CACHE.cache[c_key]['description'] \
         for c_key in sorted(GLOBAL_CACHE.cache.keys())]
    )

if '__func__' in dir(DocCache.get):
    DocCache.get.__func__.__doc__ %= DOC_LIST
else:
    DocCache.get.__doc__ %= DOC_LIST
