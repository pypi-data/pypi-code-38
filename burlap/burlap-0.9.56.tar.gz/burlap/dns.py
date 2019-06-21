from __future__ import print_function

import time
from pprint import pprint

import six

from burlap.constants import *
from burlap import Satchel
from burlap.decorators import task, runs_once
from burlap.common import print_success

GODADDY = 'godaddy'
BACKENDS = (
    GODADDY,
)

class DNSSatchel(Satchel):
    """
    Manages DNS zone records.
    """

    name = 'dns'

    def set_defaults(self):
        self.zones = []

    def update_dns_godaddy(self, domain, record_type, record):
        from godaddypy import Client, Account
        from godaddypy.client import BadResponse

        def get_domains(client):
            a = set()
            for d in client.get_domains():
                time.sleep(0.25)
                a.add(d)
            return a

        key = self.genv.godaddy_api_keys[domain]['key']
        secret = self.genv.godaddy_api_keys[domain]['secret']
        my_acct = Account(api_key=key, api_secret=secret)
        client = Client(my_acct)
        #allowed_domains = set(client.get_domains())
        allowed_domains = get_domains(client)
#         print('allowed_domains:', allowed_domains)
        assert domain in allowed_domains, \
            'Domain %s is invalid this account. Only domains %s are allowed.' % (domain, ', '.join(sorted(allowed_domains)))
        #client.add_record(domain, {'data':'1.2.3.4','name':'test','ttl':3600, 'type':'A'})
        print('Adding record:', domain, record_type, record)
        if not self.dryrun:
            try:
                max_retries = 10
                for retry in six.moves.range(max_retries):
                    try:
                        client.add_record(
                            domain,
                            {
                                'data': record.get('ip', record.get('alias')),
                                'name': record['name'],
                                'ttl': record['ttl'],
                                'type': record_type.upper()
                            })
                        print_success('Record added!')
                        break
                    except ValueError as exc:
                        print('Error adding DNS record on attempt %i of %i: %s' % (retry+1, max_retries, exc))
                        if retry + 1 == max_retries:
                            raise
                        time.sleep(3)
            except BadResponse as e:
                if e._message['code'] == 'DUPLICATE_RECORD':
                    print('Ignoring duplicate record.')
                else:
                    raise

    def get_last_zonefile(self, fn):
        lm = self.last_manifest
        zone_files = lm.zone_files or {}
        return zone_files.get(fn)

    @task
    @runs_once
    def update_dns(self):
        from blockstack_zones import parse_zone_file
        #from blockstack_zones import parse_zone_file
        r = self.local_renderer
        for zone_data in r.env.zones:
            zone_file = zone_data['file']
            domain = zone_data['domain']
            backend = zone_data['backend']
            types = zone_data['types']
            if backend not in BACKENDS:
                raise NotImplementedError('Unsupported backend: %s' % backend)
            print('Processing zone file %s for domain %s.' % (zone_file, domain))
            zone_data = open(zone_file).read()
            zone_data = parse_zone_file(zone_data)
            if self.verbose:
                pprint(dict(zone_data), indent=4)

            #TODO:add differential update using get_last_zonefile()

            # Only update record types we're specifically incharge of managing.
            for record_type in types:
                record_type = record_type.lower()
                for record in zone_data.get(record_type):
                    getattr(self, 'update_dns_%s' % backend)(domain=domain, record_type=record_type, record=record)
                    #break
                #break

    def record_manifest(self):
        r = self.local_renderer
        manifest = super(DNSSatchel, self).record_manifest()
        manifest['zone_files'] = {}
        for zone_data in r.env.zones:
            zone_file = zone_data['file']
            manifest['zone_files'][zone_file] = open(zone_file).read()
        return manifest

    @task
    def configure(self):
        if self.genv.hosts and self.genv.host_string == self.genv.hosts[0]:
            self.update_dns()

dns = DNSSatchel()
