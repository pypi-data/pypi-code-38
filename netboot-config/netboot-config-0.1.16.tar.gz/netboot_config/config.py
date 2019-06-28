import ipaddress
from typing import Optional, List

import yaml

from .network import HostGroup, Host


class Config(object):

    def __init__(self, config_file: str):

        self.hosts = []
        self.static_hosts = []
        self.netboot_host = None
        self.network_prefixes = {}

        with open(config_file, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            self.netboot_host = data_loaded['netboot']['host']

            for host_group_entry in data_loaded['hostgroups']:
                host_group = self.create_host_group(host_group_entry)

                for host_entry in host_group_entry['hosts']:
                    self.map_entry(host_entry, host_group)

                self.hosts += host_group.hosts()

            for host_group_entry in data_loaded['hosts']:
                host_group = self.create_host_group(host_group_entry)

                for host_entry in host_group_entry['hosts']:
                    self.map_entry(host_entry, host_group)

                self.static_hosts += host_group.hosts()

    def create_host_group(self, host_group_entry):
        prefix_ = host_group_entry['prefix']
        cidr_ = host_group_entry['cidr']
        self.network_prefixes[cidr_] = prefix_
        host_group = HostGroup(prefix_, cidr_)
        return host_group

    def map_entry(self, host_entry, host_group):
        offset_ = host_entry['offset']
        count_ = host_entry['count'] if 'count' in host_entry else 1

        if 'alias' in host_entry:
            aliases_ = (host_entry['alias'],)
        elif 'aliases' in host_entry:
            aliases_ = tuple(host_entry['aliases'])
        else:
            aliases_ = None

        if 'config' in host_entry:
            config_ = [(config_entry['source'], config_entry['target']) for config_entry in host_entry['config']]
        else:
            config_ = None

        image_type_ = host_entry['image_type'] if 'image_type' in host_entry else None

        host_group.add_hosts(offset_, count_, aliases_, image_type_, config_)

    @property
    def all_hosts(self) -> List[Host]:
        return self.hosts + self.static_hosts

    def get_host(self, ip_address_string: str) -> Optional[Host]:
        ip_address = ipaddress.IPv4Address(ip_address_string)
        for cidr, prefix in self.network_prefixes.items():
            network = ipaddress.IPv4Network(cidr)
            if ip_address in network:
                return Host(prefix, network, ip_address)
        return None
