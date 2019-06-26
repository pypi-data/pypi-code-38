import ipaddress

import yaml

from .network import HostGroup, Host, SpecificHost


class Config(object):

    def __init__(self, config_file: str):

        self.hosts = []
        self.static_hosts = []
        self.netboot_host = None

        with open(config_file, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            self.netboot_host = data_loaded['netboot']['host']

            for data in data_loaded['hostgroups']:
                host_group = HostGroup(data['prefix'], data['cidr'])
                for image in data['images']:
                    host_group.add_hosts(image['image_type'], image['offset'], image['count'])

                self.hosts += host_group.hosts()

            for host_entry in data_loaded['hosts']:
                prefix = host_entry['prefix']
                host_ip = ipaddress.IPv4Address(host_entry['address'])
                aliases = tuple(host_entry['aliases']) if 'aliases' in host_entry else None

                self.static_hosts += [SpecificHost(prefix, host_ip, None, aliases)]

    @property
    def all_hosts(self):
        return self.hosts + self.static_hosts
