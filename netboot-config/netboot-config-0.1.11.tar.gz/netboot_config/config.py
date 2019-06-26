import yaml

from .network import HostGroup


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

            for host_name, data in data_loaded['hosts'].items():
                if isinstance(data, dict):
                    host_ip = data['address']
                    aliases = tuple(data['aliases'])
                else:
                    host_ip = data
                    aliases = ()
                self.static_hosts += [(host_ip, (host_name,) + aliases)]
