
import json
import os
import sys

from bisect import bisect_left
from datetime import datetime
from netaddr.ip import IPAddress
from operator import attrgetter

from .subnet import Network

if sys.platform == 'darwin':
    CACHE_DIR = os.path.expanduser('~/Library/Caches/netlookup')
else:
    CACHE_DIR = os.path.expanduser('~/.cache/netlookup')


class AddressCacheError(Exception):
    pass


class Prefix(Network):
    """
    Named network prefix for specific vendor and service
    """
    type = 'generic'
    extra_attributes = []

    def __init__(self, network, data=None):
        super().__init__(network)

        if data is not None:
            for attr in self.extra_attributes:
                if attr in data:
                    setattr(self, attr, data[attr])

    def __repr__(self):
        return '{} {}'.format(self.type, self.cidr)

    def __str__(self):
        return self.__repr__()

    def as_dict(self):
        """
        Format prefix object as dictionary

        Extend in child class to get prefix type specific data
        """
        data = {
            'type': self.type,
            'cidr': str(self.cidr)
        }
        for attr in self.extra_attributes:
            data[attr] = getattr(self, attr)
        return data


class AddressPrefixCache:
    """
    Common base class for network address prefix caching and lookups
    """
    cache_filename = None
    prefix_class = Prefix

    def __init__(self, cache_directory=CACHE_DIR):
        self.cache_directory = cache_directory
        self.updated = None
        self.prefixes = []
        self.__iter_index__ = None

        if not os.path.isdir(CACHE_DIR):
            try:
                os.makedirs(CACHE_DIR)
            except Exception as e:
                raise AddressCacheError('Error creating directory {}: {}'.format(CACHE_DIR, e))

        if os.path.isfile(self.cache_file):
            self.load()

    def __iter__(self):
        return self

    def __next__(self):
        if not self.prefixes:
            self.fetch()
        if self.__iter_index__ is None:
            self.__iter_index__ = 0
        try:
            item = self.prefixes[self.__iter_index__]
            self.__iter_index__ += 1
            return item
        except IndexError:
            self.__iter_index__ = None
            raise StopIteration

    @property
    def cache_file(self):
        """
        Filename for prefix data cache file
        """
        return os.path.join(self.cache_directory, self.cache_filename)

    def fetch(self):
        raise NotImplementedError('fetch() must be implemented in child class')

    def as_dict(self):
        """
        Return all prefixes as dictionary
        """
        return {
            'updated': self.updated.isoformat() if self.updated else None,
            'prefixes': [prefix.as_dict() for prefix in self.prefixes]
        }

    def load(self):
        """
        Load local cache file
        """
        if not os.path.isfile(self.cache_file):
            return

        self.prefixes = []
        try:
            with open(self.cache_file, 'r') as fd:
                data = json.loads(fd.read())
        except Exception as e:
            raise AddressCacheError('Error reading cache file {}: {}'.format(
                self.cache_file,
                e
            ))

        try:
            self.updated = datetime.fromisoformat(data['updated'])
            for record in data['prefixes']:
                prefix = self.prefix_class(record['cidr'], record)
                self.prefixes.append(prefix)
        except Exception as e:
            raise AddressCacheError('Error loading data from cache file {}: {}'.format(
                self.cache_file,
                e
            ))

    def save(self):
        """
        Save data to cache file
        """
        if not self.cache_file:
            return

        try:
            with open(self.cache_file, 'w') as fd:
                fd.write('{}\n'.format(json.dumps(self.as_dict(), indent=2)))
        except Exception as e:
            raise AddressCacheError('Error writing cache file {}: {}'.format(
                self.cache_file,
                e
            ))

    def find(self, value):
        """
        Find address in prefixes
        """
        address = IPAddress(value)
        next = bisect_left(self.prefixes, address)
        if next > 0:
            prefix = self.prefixes[next - 1]
            if address == prefix or address in prefix:
                return prefix
        return None


class Prefixes:
    """
    Loader and lookup for known IP address prefix caches
    """
    def __init__(self, cache_directory=CACHE_DIR):
        from .cloud.aws import AWS
        from .cloud.azure import Azure
        from .cloud.gcp import GCP
        from .cloud.google import GoogleServices

        self.vendors = []
        self.prefixes = []

        self.vendors.append(AWS(cache_directory=cache_directory))
        self.vendors.append(Azure(cache_directory=cache_directory))
        self.vendors.append(GCP(cache_directory=cache_directory))
        self.vendors.append(GoogleServices(cache_directory=cache_directory))

        self.load()

    def update(self):
        """
        Fetch and update cached prefix data
        """
        for vendor in self.vendors:
            try:
                vendor.fetch()
                vendor.save()
            except Exception as e:
                raise AddressCacheError('Error updating {} data: {}'.format(vendor, e))
        self.load()

    def load(self):
        """
        Load cached prefixes
        """
        self.prefixes = []
        for vendor in self.vendors:
            vendor.load()
            for prefix in vendor.prefixes:
                self.prefixes.append(prefix)
        self.prefixes.sort(key=attrgetter('value'))

    def filter_type(self, value):
        """
        Filter prefixes by type
        """
        return [prefix for prefix in self.prefixes if prefix.type == value]

    def find(self, value):
        """
        Find address in prefixes
        """
        address = IPAddress(value)
        next = bisect_left(self.prefixes, address)
        if next > 0:
            try:
                prefix = self.prefixes[next]
                if address.value == prefix.value or address in prefix:
                    return prefix
            except IndexError:
                pass
            prefix = self.prefixes[next - 1]
            if address.value == prefix.value or address in prefix:
                return prefix
        return None
