
from netaddr.ip import IPNetwork, IPAddress
from netaddr.core import AddrFormatError


class Network(IPNetwork):
    """
    Extend IPSubnet with some custom attributes
    """

    def __eq__(self, other):
        if isinstance(other, Network):
            return self.value == other.value and self.prefixlen == other.prefixlen
        if isinstance(other, IPAddress):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, Network) or isinstance(other, IPAddress):
            return self.value < other.value
        elif isinstance(other, int):
            return self.value < other

    def __le__(self, other):
        if isinstance(other, Network) or isinstance(other, IPAddress):
            return self.value <= other.value
        elif isinstance(other, int):
            return self.value <= other

    def __gt__(self, other):
        if isinstance(other, Network) or isinstance(other, IPAddress):
            return self.last > other.value
        elif isinstance(other, int):
            return self.value > other

    def __ge__(self, other):
        if isinstance(other, Network) or isinstance(other, IPAddress):
            return self.value >= other.value
        elif isinstance(other, int):
            return self.value >= other

    @property
    def total_hosts(self):
        """
        Return total number of available hosts in subnet, excluding network and broadcast
        addresses
        """
        if self.version == 4:
            if self.prefixlen == 31:
                return 2
            if self.prefixlen == 32:
                return 1
        if self.version == 6:
            if self.prefixlen == 127:
                return 2
            if self.prefixlen == 128:
                return 1
        return self.size - 2

    @property
    def first_host(self):
        """
        Return first available host in network, excluding network address
        """
        if self.version == 4:
            if self.prefixlen == 31:
                return IPAddress(self.first)
            if self.prefixlen == 32:
                return None
        if self.version == 6:
            if self.prefixlen == 127:
                return IPAddress(self.first)
            if self.prefixlen == 128:
                return None
        return IPAddress(self.first + 1)

    @property
    def last_host(self):
        """
        Return last available host in network, excluding broadcast address
        """
        if self.version == 4:
            if self.prefixlen == 31:
                return IPAddress(self.last)
            if self.prefixlen == 32:
                return None
        if self.version == 6:
            if self.prefixlen == 127:
                return IPAddress(self.last)
            if self.prefixlen == 128:
                return None
        return IPAddress(self.last - 1)

    @property
    def next_subnet_prefix(self):
        """
        Return next subnet prefix size, i.e. smaller prefix than this

        May return None when item is already a host only network
        """
        if self.version == 4:
            if self.prefixlen == 32:
                return None
        if self.version == 6:
            if self.prefixlen == 128:
                return None
        return self.prefixlen + 1

    @property
    def parent_subnet_prefix(self):
        """
        Return parent subnet prefix size, i.e. one larger prefix than this

        May return None when item is already 0
        """
        if self.prefixlen == 0:
            return None
        return self.prefixlen - 1

    def subnet(self, prefixlen):
        """
        Return subnets split by specified prefix

        Adds extra validation for prefixlen, checking the value is not out off scope
        based on address type
        """
        prefixlen = int(prefixlen)
        if self.version == 4:
            if prefixlen < 0 or prefixlen > 32:
                raise AddrFormatError('Invalid IPv4 prefix len')

        if self.version == 6:
            if prefixlen < 0 or prefixlen > 128:
                raise AddrFormatError('Invalid IPv4 prefix len')

        if prefixlen <= self.prefixlen:
            raise AddrFormatError('Split mask {} is not valid for prefixlen {}'.format(
                prefixlen,
                self.prefixlen
            ))

        return super().subnet(prefixlen)
