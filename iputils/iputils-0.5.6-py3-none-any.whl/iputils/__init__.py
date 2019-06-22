#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# date:        2019/6/6
# author:      he.zhiming
#

from __future__ import (absolute_import, unicode_literals)

import ipaddress

from ipaddress import ip_interface, ip_network
from ipaddress import _IPv4Constants, _IPv6Constants

_SPECIAL_NETWORKS_IPV4 = frozenset((
    _IPv4Constants._loopback_network,
    _IPv4Constants._multicast_network,
    _IPv4Constants._reserved_network,
    _IPv4Constants._unspecified_address
))
_SPECIAL_NETWORKS_IPV6 = frozenset(
    [_IPv6Constants._multicast_network,
     _IPv6Constants._sitelocal_network] + _IPv6Constants._reserved_networks
)


def _is_ip_address(ipobj):
    return isinstance(ipobj, (ipaddress.IPv4Address, ipaddress.IPv6Address))


def _is_ip_network(ipobj):
    return isinstance(ipobj, (ipaddress.IPv4Network, ipaddress.IPv6Network))


class IPException(Exception):
    pass


class IPUtils:
    @classmethod
    def get_special_networks(cls, version=4):
        if version == 4:
            return [str(item) for item in _SPECIAL_NETWORKS_IPV4]
        if version == 6:
            return [str(item) for item in _SPECIAL_NETWORKS_IPV6]

    @classmethod
    def get_ip_amount(cls, network, strict=False):
        net = ip_network(network, strict=strict)

        return net.num_addresses

    @classmethod
    def is_valid(cls, ip):
        try:
            ip_interface(ip)
            return True
        except ValueError:
            return False

    @classmethod
    def is_ipv4(cls, ip):
        return ip_interface(ip).version == 4

    @classmethod
    def is_ipv6(cls, ip):
        return ip_interface(ip).version == 6

    @classmethod
    def is_network(cls, ip, strict=True):
        try:
            ip_network(ip, strict=strict)
            return True
        except ValueError:
            return False

    @classmethod
    def get_network_addr(cls, ip):
        return str(ip_interface(ip).network)

    @classmethod
    def get_broadcast_addr(cls, ip):
        n = ip_interface(ip).network

        return str(n.broadcast_address)

    @classmethod
    def with_prefix(cls, ip):
        return ip_interface(ip).with_prefixlen

    @classmethod
    def with_netmask(cls, ip):
        return ip_interface(ip).with_netmask

    @classmethod
    def get_belong_special_network(cls, ip):
        """获取属于哪个特殊网络

        :param ip:
        :return:
        """
        ipint = cls.ip_to_int(ip)

        if cls.is_v4(ip):
            for net in _SPECIAL_NETWORKS_IPV4:
                if _is_ip_address(net):
                    if ipint == int(net):
                        return str(net)
                if cls._is_in_network(ip, net):
                    return str(net)

        if cls.is_v6(ip):
            for net in _SPECIAL_NETWORKS_IPV6:
                if _is_ip_address(net):
                    if ipint == int(net):
                        return str(net)
                if cls._is_in_network(ip, net):
                    return str(net)

        return None

    @classmethod
    def is_v4(cls, ip):
        return ip_interface(ip).version == 4

    @classmethod
    def is_v6(cls, ip):
        return ip_interface(ip).version == 6

    @classmethod
    def ip_to_int(cls, ip):
        return int(ip_interface(ip))

    @classmethod
    def int_to_ip(cls, number, version=4):
        if version == 4:
            return str(ipaddress.IPv4Interface(number).ip)

        if version == 6:
            return str(ipaddress.IPv6Interface(number).ip)

        raise IPException(f'not support version: {version}')

    @classmethod
    def is_in_network(cls, ip, network, strict=True):
        """某IP是否在某网络内

        :param ip:
        :param network:
        :param strict: 严格的网络地址
        :return:
        """
        return cls._is_in_network(ip, ipaddress.ip_network(network, strict=strict))

    @classmethod
    def is_ips_equal(cls, *ips):
        return len({cls.ip_to_int(ip) for ip in ips}) == 1

    @classmethod
    def _is_in_network(cls, ip, network_obj):
        ipint = cls.ip_to_int(ip)

        if _is_ip_address(network_obj):
            return ipint == int(network_obj)

        return int(network_obj[0]) <= ipint <= int(network_obj[-1])
