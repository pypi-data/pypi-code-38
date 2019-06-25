import requests


class FalconIntelligence:
    """Class containing handy methods common to working with the CrowdStrike Falcon Intelligence API."""

    def __init__(self, api_uuid, api_key):
        self.base_url = 'https://intelapi.crowdstrike.com'
        self.ioc_url_part = '/indicator/v2/search/'
        self.api_uuid = api_uuid
        self.api_key = api_key
        self.headers = {'X-CSIX-CUSTID': self.api_uuid, 'X-CSIX-CUSTKEY': self.api_key,
                        'Content-Type': 'application/json'}

    def is_threat(self, test_object):
        """
        Check if an indicator is malicious (i.e. an active IOC in Falcon Intelligence)
        :param test_object: indicator to check
        :return: True if malicious, False if not found active in Falcon Intelligence
        """
        result = self.get_ioc_details(test_object)
        return len(result) > 0

    def get_ioc_details(self, test_object):
        """
        Get details for one specific IOC.
        :param test_object: object to search for
        :return: list of dictionaries (usually only one in the list) containing IOC details
        """
        filter = 'indicator?equal=%s' % test_object
        ioc_url = '%s%s%s' % (self.base_url, self.ioc_url_part, filter)
        json_data = requests.get(ioc_url, headers=self.headers).json()
        return json_data

    def get_iocs(self, ioc_type, filters=None, details=False, results_per_page=150000):
        """
        Get a list of IOCs from the specified type.
        :param ioc_type: type of IOC (i.e. ip, domain, etc)
        :param filters: dictionary of filters to apply
        :param details: get simple list of IOCs if False (which is default), or IOCs with details if True
        :param results_per_page: default is set to top limit of 150000
        :return: list of IOCs
        """
        if not filters:
            filter = 'type?equal=%s&perPage=%s' % (ioc_type, results_per_page)
        else:
            filter = '?type.match=%s&perPage=%s' % (ioc_type, results_per_page)
            for k in filters.keys():
                filter += '&%s.match=%s' % (k, filters[k])
        ioc_url = '%s%s%s' % (self.base_url, self.ioc_url_part, filter)
        json_data = requests.get(ioc_url, headers=self.headers).json()
        if not details:
            iocs = []
            for line in json_data:
                iocs.append(line['indicator'])
            return iocs
        return json_data
