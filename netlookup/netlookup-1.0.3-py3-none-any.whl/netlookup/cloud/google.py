
import re

from datetime import datetime
from dns import resolver
from operator import attrgetter

from ..prefixes import NetworkSet, NetworkSetError, NetworkSetItem

ADDRESS_LIST_RECORD = '_spf.google.com'
RE_INCLUDE = re.compile(r'^include:(?P<rr>.*)$')
RE_IPV4 = re.compile(r'^ip4:(?P<prefix>.*)$')
RE_IPV6 = re.compile(r'^ip6:(?P<prefix>.*)$')


class GoogleServicePrefix(NetworkSetItem):
    """
    Google services network prefix
    """
    type = 'google'


class GoogleServices(NetworkSet):
    """
    Google services address ranges

    Note: this data currently does not include information about regions
    """
    cache_filename = 'google-service-networks.json'
    loader_class = GoogleServicePrefix

    def fetch(self):
        def process_rr(rr, includes):
            res = resolver.query(rr, 'TXT')
            try:
                data = str(res.rrset[0].strings[0], 'utf-8')
            except Exception as e:
                raise NetworkSetError('Error parsing data for {}: {}'.format(rr, e))

            for field in data.split(' '):
                m = RE_IPV4.match(field)
                if m:
                    self.networks.append(self.loader_class(m.groupdict()['prefix']))
                    continue

                m = RE_IPV6.match(field)
                if m:
                    self.networks.append(self.loader_class(m.groupdict()['prefix']))
                    continue

                m = RE_INCLUDE.match(field)
                if m:
                    include = m.groupdict()['rr']
                    if include not in includes:
                        process_rr(include, includes)
                    includes.append(include)
                    continue

        self.networks = []
        includes = []
        process_rr(ADDRESS_LIST_RECORD, includes)

        self.updated = datetime.now()
        self.networks.sort(key=attrgetter('version', 'cidr'))
