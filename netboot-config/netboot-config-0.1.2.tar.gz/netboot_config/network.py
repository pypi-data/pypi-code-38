import ipaddress
from typing import List


class Host(object):

    def __init__(self, name_prefix: str, address: ipaddress.IPv4Address, image_type: str):
        self.name_prefix = name_prefix

        value = address._ip
        first = value % 256
        value //= 256
        second = value % 256
        value //= 256
        third = value % 256
        value //= 256
        fourth = value % 256
        self._address = (fourth, third, second, first)

        self._image_type = image_type


    def ipv4_address(self) -> str:
        return ".".join((str(x) for x in self._address))

    def ipv4_address_hex(self) -> str:
        return "".join(('{:02X}'.format(x) for x in self._address))

    def host_name(self):
        return self.name_prefix + str(self._address[-1])

    def image_type(self) -> str:
        return self._image_type

    def __str__(self):
        return str(self._address)


class HostGroup(object):

    def __init__(self, name_prefix: str, cidr_string: str):
        self.network = ipaddress.ip_network(cidr_string)
        self.name_prefix = name_prefix
        self._hosts = []

    def add_hosts(self, image_type: str, machine_offset: int, machine_count: int) -> None:
        self._hosts += (Host(self.name_prefix, x, image_type) for i, x in enumerate(self.network.hosts())
                       if machine_offset <= i < machine_offset + machine_count)

    def hosts(self) -> List[Host]:
        return self._hosts
