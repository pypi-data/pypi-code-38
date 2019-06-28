import json
from mcneelat.pyutils.confutils import AbstractLogUtils
import requests


class SearchLight(AbstractLogUtils):
    """Class containing handy methods common to working with the Digital Shadows SearchLight API."""

    def __init__(self, api_id, api_key, verbose=True):
        """
        Initialize class.
        :param api_id: ID to identify self when sending API requests
        :param api_key: key to authenticate ID when sending API requests
        :param verbose: whether or not to print log messages
        """
        self.api_id = api_id
        self.api_key = api_key
        self.base_url = 'https://portal-digitalshadows.com/api'
        self.search_url = '%s/search/find' % self.base_url
        AbstractLogUtils.__init__(self, verbose)

    def search(self, search_text, exact_match=False, results_per_page=1000, offset=0):
        """
        Search for objects matching the given query.
        :param search_text: text to search for
        :param exact_match: whether or not to search for an exact match of the text; defaults to False
        :param results_per_page: maximum results per page; defaults to actual maximum of 1000
        :param offset: offset for pagination
        :return: results in JSON format
        """
        if exact_match:
            search_text = '"%s"' % search_text
        query = {'query': search_text, 'pagination': {'size': results_per_page, 'offset': offset}}
        self.log('[*] Searching for query %s...' % query['query'])
        results = requests.post(self.search_url, data=json.dumps(query), auth=(self.api_id, self.api_key),
                                headers={'Content-Type': 'application/json'})
        return results.json()
