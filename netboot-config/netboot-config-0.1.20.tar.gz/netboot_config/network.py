import ipaddress
from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Optional


class HostMeta(metaclass=ABCMeta):

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


class DefaultHost(HostMeta):

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


class Host(HostMeta):

    def __init__(self, name_prefix: str, network: ipaddress.IPv4Network, address: ipaddress.IPv4Address, image_type: Optional[str] = None,
                 aliases: Optional[List[str]] = None, config: Optional[List[Tuple[str]]] = None, address_digits=2):
        self.host_name_template = name_prefix + "{:0" + str(address_digits) + "}"

        self._address = address
        self._network = network

        self._image_type = image_type
        self._aliases = tuple(aliases) if aliases is not None else ()
        self._config = tuple(config) if config is not None else ()

    @property
    def ipv4_address(self) -> str:
        return str(self._address)

    @property
    def reverse_pointer(self) -> str:
        return self._address.reverse_pointer

    @property
    def ipv4_address_hex(self) -> str:
        return "{:08X}".format(self._address._ip)

    @property
    def host_name(self):
        addr_mask = (1 << 32 - self._network.prefixlen) - 1
        return self.host_name_template.format(self._address._ip & addr_mask)

    @property
    def image_type(self) -> str:
        return self._image_type

    @property
    def aliases(self) -> Tuple[str]:
        return self._aliases

    @property
    def config(self):
        return self._config

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
                  image_type: Optional[str] = None, config: Optional[Tuple[str]] = None) -> None:
        self._hosts += (Host(self.name_prefix, self.network, x, image_type, aliases, config) for i, x in
                        enumerate(self.network.hosts())
                        if machine_offset <= i + 1 < machine_offset + machine_count)

    def hosts(self) -> List[HostMeta]:
        return self._hosts
