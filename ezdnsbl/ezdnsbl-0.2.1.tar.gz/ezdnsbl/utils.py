#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import win_inet_pton
except ImportError:
    pass
import socket
import re


def get_data_type(data):
    """ Try and figure out what DNSBL data_type the given data fits """
    try:
        socket.inet_pton(socket.AF_INET, data)
        return 'ipv4'
    except socket.error:
        pass

    try:
        socket.inet_pton(socket.AF_INET6, data)
        return 'ipv6'
    except socket.error:
        pass

    try:
        assert(len(re.match(r"^([\d\.].*/[\d]{1,2})$", data).groups()) == 1)
        return 'ipv4_subnet'
    except AttributeError:
        pass

    try:
        assert(len(re.match(r"^([\d\:].*/[\d]{1,3})$", data).groups()) == 1)
        return 'ipv6_subnet'
    except AttributeError:
        pass

    try:
        assert(len(re.match(r"^([Aa][Ss][Nn]?[0-9]{1,8})$", data).groups()) == 1)
        return 'asn'
    except AttributeError:
        pass

    try:
        assert(len(re.match(r"^([a-fA-F\d]{32,128})$", data).groups()) == 1)
        return 'hash'
    except AttributeError:
        pass

    try:
        assert(len(re.match(r"^([a-zA-Z-\d\.]{2,})$", data).groups()) == 1)
        return 'domain'
    except AttributeError:
        pass

    return 'unknown'


def pluralize(singular, plural, number):
    if number == 1 or number == -1:
        return singular
    else:
        return plural
