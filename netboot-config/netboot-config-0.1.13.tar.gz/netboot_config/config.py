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

            for host_group_entry in data_loaded['hostgroups']:
                host_group = HostGroup(host_group_entry['prefix'], host_group_entry['cidr'])

                for host_entry in host_group_entry['hosts']:
                    self.map_entry(host_entry, host_group)

                self.hosts += host_group.hosts()

            for host_group_entry in data_loaded['hosts']:
                host_group = HostGroup(host_group_entry['prefix'], host_group_entry['cidr'])

                for host_entry in host_group_entry['hosts']:
                    self.map_entry(host_entry, host_group)

                self.static_hosts += host_group.hosts()

    def map_entry(self, host_entry, host_group):
        offset_ = host_entry['offset']
        count_ = host_entry['count'] if 'count' in host_entry else 1

        if 'alias' in host_entry:
            aliases_ = (host_entry['alias'],)
        elif 'aliases' in host_entry:
            aliases_ = tuple(host_entry['aliases'])
        else:
            aliases_ = None

        image_type_ = host_entry['image_type'] if 'image_type' in host_entry else None

        host_group.add_hosts(offset_, count_, aliases_, image_type_)


    @property
    def all_hosts(self):
        return self.hosts + self.static_hosts
