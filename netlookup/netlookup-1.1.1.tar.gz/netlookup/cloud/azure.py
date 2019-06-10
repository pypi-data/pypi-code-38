
import json
import requests

from datetime import datetime
from operator import attrgetter

from ..prefixes import NetworkSet, NetworkSetError, NetworkSetItem

AZURE_SERVICES_URL = 'https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20190603.json' # noqa E501


class AzurePrefix(NetworkSetItem):
    """
    Azure network prefix with region and service details
    """
    type = 'azure'
    extra_attributes = ('id', 'name', 'service', 'region')

    def __init__(self, network, data=None):
        self.id = None
        self.name = None
        self.region = None
        self.service = None
        super().__init__(network, data)

    def __repr__(self):
        return '{} {} {}'.format(self.type, self.name, self.cidr)

    def as_dict(self):
        """
        Return azure prefix with extra details
        """
        data = super().as_dict()
        data.update({
            'id': self.id,
            'name': self.name,
            'service': self.service,
            'region': self.region,
        })
        return data


class Azure(NetworkSet):
    """
    Azure address networks
    """
    type = 'azure'
    cache_filename = 'azure-networks.json'
    loader_class = AzurePrefix

    def fetch(self):
        """
        Fetch Azure IP range data
        """
        try:
            res = requests.get(AZURE_SERVICES_URL)
            if res.status_code != 200:
                raise ValueError('HTTP status code {}'.format(res.status_code))
        except Exception as e:
            raise NetworkSetError('Error fetching AWS IP ranges: {}'.format(e))

        try:
            data = json.loads(res.content)
        except Exception as e:
            raise NetworkSetError('Error loading AWS IP range data: {}'.format(e))

        self.networks = []
        for section in data['values']:
            kwargs = {
                'id': section['id'],
                'name': section['name'],
                'service': section['properties']['systemService'],
                'region': section['properties']['region'],
            }
            for prefix in section['properties']['addressPrefixes']:
                self.networks.append(self.loader_class(prefix, kwargs))

        self.updated = datetime.now()
        self.networks.sort(key=attrgetter('version', 'region', 'service'))
