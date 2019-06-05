import ipaddress
from abc import ABCMeta, abstractmethod
from typing import List


class Host(metaclass=ABCMeta):

    @property
    @abstractmethod
    def image_type(self):
        pass

    @property
    @abstractmethod
    def host_name(self):
        pass

    @property
    @abstractmethod
    def ipv4_address(self):
        pass

    @property
    @abstractmethod
    def ipv4_address_hex(self):
        pass


class DefaultHost(Host):

    def __init__(self, image_type):
        self._image_type = image_type

    @property
    def image_type(self):
        return self._image_type

    @property
    def host_name(self):
        return None

    @property
    def ipv4_address(self):
        return None

    @property
    def ipv4_address_hex(self):
        return "default"


class SpecificHost(Host):

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

    @property
    def ipv4_address(self) -> str:
        return ".".join((str(x) for x in self._address))

    @property
    def ipv4_address_hex(self) -> str:
        return "".join(('{:02X}'.format(x) for x in self._address))

    @property
    def host_name(self):
        return self.name_prefix + str(self._address[-1])

    @property
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
        self._hosts += (SpecificHost(self.name_prefix, x, image_type) for i, x in enumerate(self.network.hosts())
                        if machine_offset <= i + 1 < machine_offset + machine_count)

    def hosts(self) -> List[Host]:
        return self._hosts
