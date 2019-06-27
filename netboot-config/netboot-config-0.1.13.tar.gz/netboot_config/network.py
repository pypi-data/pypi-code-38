import ipaddress
from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Optional


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

    @property
    @abstractmethod
    def aliases(self):
        pass

    @property
    @abstractmethod
    def entry(self):
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

    @property
    def aliases(self):
        return []

    @property
    def entry(self):
        return ""


class SpecificHost(Host):

    def __init__(self, name_prefix: str, address: ipaddress.IPv4Address, image_type: Optional[str]=None, aliases: Optional[List[str]]=None):
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
        self._aliases = tuple(aliases) if aliases is not None else ()

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

    @property
    def aliases(self) -> Tuple[str]:
        return self._aliases

    @property
    def entry(self) -> str:
        return "{}\t{}".format(self.ipv4_address, " ".join((self.host_name,) + self.aliases))

    def __str__(self):
        return str(self._address)


class HostGroup(object):

    def __init__(self, name_prefix: str, cidr_string: str):
        self.network = ipaddress.ip_network(cidr_string)
        self.name_prefix = name_prefix
        self._hosts = []

    def add_hosts(self, machine_offset: int, machine_count: int, aliases: Optional[List[str]] = None,
                  image_type: Optional[str] = None) -> None:
        self._hosts += (SpecificHost(self.name_prefix, x, image_type, aliases) for i, x in enumerate(self.network.hosts())
                        if machine_offset <= i + 1 < machine_offset + machine_count)

    def hosts(self) -> List[Host]:
        return self._hosts
