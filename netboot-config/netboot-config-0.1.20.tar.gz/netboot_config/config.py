import ipaddress
from typing import Optional, List, ValuesView

import yaml

from .network import HostGroup, Host


class Config(object):

    def __init__(self, config_file: str):

        self._hosts = {}
        self._static_hosts = {}
        self.netboot_host = None
        self.network_prefixes = {}

        with open(config_file, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            self.netboot_host = data_loaded['netboot']['host']

            for host_group_entry in data_loaded['hostgroups']:
                host_group = self.create_host_group(host_group_entry)

                for host_entry in host_group_entry['hosts']:
                    self.map_entry(host_entry, host_group)

                self._hosts.update({host.ipv4_address: host for host in host_group.hosts()})

            for host_group_entry in data_loaded['hosts']:
                host_group = self.create_host_group(host_group_entry)

                for host_entry in host_group_entry['hosts']:
                    self.map_entry(host_entry, host_group)

                self._static_hosts.update({host.ipv4_address: host for host in host_group.hosts()})

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
    def hosts(self) -> List[Host]:
        return list(self._hosts.values())

    @property
    def static_hosts(self) -> List[Host]:
        return list(self._static_hosts.values())

    @property
    def all_hosts(self) -> List[Host]:
        return self.hosts + self.static_hosts

    @property
    def aliases(self):
        aliases = []
        for host in self.all_hosts:
            host_name = host.host_name
            for alias in host.aliases:
                aliases.append((alias, host_name))
        return aliases

    def get_host(self, ip_address_string: str) -> Optional[Host]:
        if ip_address_string in self._static_hosts:
            return self._static_hosts[ip_address_string]

        if ip_address_string in self._hosts:
            return self._hosts[ip_address_string]

        ip_address = ipaddress.IPv4Address(ip_address_string)
        for cidr, prefix in self.network_prefixes.items():
            network = ipaddress.IPv4Network(cidr)
            if ip_address in network:
                return Host(prefix, network, ip_address)
        return None
