# -*- coding: utf-8 -*-
# Description: validation functions

from ipaddress import (AddressValueError, NetmaskValueError,
                       ip_address, IPv4Address, IPv6Address,
                       ip_network, IPv4Network, IPv6Network)


def valid_ip(ip,
             method=ip_address):

    try:
        method(u'{ip}'.format(ip=ip))
        return True

    except (ValueError, AddressValueError):
        return False


def valid_ipv4(ip):
    return valid_ip(ip=ip,
                    method=IPv4Address)


def valid_ipv6(ip):
    return valid_ip(ip=ip,
                    method=IPv6Address)


def valid_ip_network(network,
                     method=ip_network,
                     strict=True):

    try:
        method(u'{net}'.format(net=network),
               strict=strict)
        return True

    except (ValueError, TypeError, AddressValueError, NetmaskValueError):
        return False


def valid_ipv4_network(*args,
                       **kwargs):
    return valid_ip_network(method=IPv4Network,
                            *args,
                            **kwargs)


def valid_ipv6_network(*args,
                       **kwargs):
    return valid_ip_network(method=IPv6Network,
                            *args,
                            **kwargs)
