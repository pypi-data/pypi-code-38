
import json
import requests

from datetime import datetime
from operator import attrgetter

from ..prefix import AddressPrefixCache, AddressCacheError, Prefix

AWS_IP_RANGES_URL = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
SKIP_SERVICE_NAMES = (
    'AMAZON',
)


class AWSPrefix(Prefix):
    """
    AWS network prefix with region and service details
    """
    type = 'aws'
    extra_attributes = ('region', 'services')

    def __init__(self, network, data=None):
        self.region = None
        self.services = []
        super().__init__(network, data)

    def __repr__(self):
        return '{} {} {}'.format(self.type, self.region, self.cidr)


class AWS(AddressPrefixCache):
    """
    AWS address prefixes
    """
    cache_filename = 'aws-prefixes.json'
    prefix_class = AWSPrefix

    @property
    def regions(self):
        """
        Return all detected regions
        """
        return sorted(set(prefix.region for prefix in self.prefixes))

    def fetch(self):
        """
        Fetch AWS IP range data
        """

        try:
            res = requests.get(AWS_IP_RANGES_URL)
            if res.status_code != 200:
                raise ValueError('HTTP status code {}'.format(res.status_code))
        except Exception as e:
            raise AddressCacheError('Error fetching AWS IP ranges: {}'.format(e))

        try:
            data = json.loads(res.content)
        except Exception as e:
            raise AddressCacheError('Error loading AWS IP range data: {}'.format(e))

        self.updated = datetime.fromtimestamp(int(data['syncToken']))

        prefixes = {}
        for item in data['prefixes']:
            prefix = self.prefix_class(item['ip_prefix'], item)
            if prefix.cidr not in prefixes:
                prefixes[prefix.cidr] = prefix
            if item['service'] not in SKIP_SERVICE_NAMES and item['service'] not in prefixes[prefix.cidr].services:
                prefixes[prefix.cidr].services.append(item['service'])

        for item in data['ipv6_prefixes']:
            prefix = self.prefix_class(item['ipv6_prefix'], item)
            if prefix.cidr not in prefixes:
                prefixes[prefix.cidr] = prefix
            if item['service'] not in SKIP_SERVICE_NAMES and item['service'] not in prefixes[prefix.cidr].services:
                prefixes[prefix.cidr].services.append(item['service'])

        self.prefixes = list(prefixes.values())
        self.prefixes.sort(key=attrgetter('version', 'region', 'services', 'cidr'))
