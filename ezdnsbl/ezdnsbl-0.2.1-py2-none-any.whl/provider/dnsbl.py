#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dns.resolver
from dns import reversename
import socket
import re

__author__ = "c0nch0b4r"
__version__ = "0.1.3"
__email__ = "lp1.on.fire@gmail.com"
__all__ = ['DNSBL_Base']

# To-Do:


def getType(data):
    """ Try and figure out what DNSBL data_type the given data fits """
    try:
        socket.inet_pton(socket.AF_INET, data)
        return 'ipv4'
    except:
        pass

    try:
        socket.inet_pton(socket.AF_INET6, data)
        return 'ipv6'
    except:
        pass

    try:
        len(re.match(r"^([\d\.].*/[\d]{1,2})$", data).groups()) == 1
        return 'ipv4_subnet'
    except:
        pass

    try:
        len(re.match(r"^([\d\:].*/[\d]{1,3})$", data).groups()) == 1
        return 'ipv6_subnet'
    except:
        pass

    try:
        len(re.match(r"^([Aa][Ss][0-9]{1,8})$", data).groups()) == 1
        return 'asn'
    except:
        pass

    try:
        len(re.match(r"^([a-fA-F\d]{32,128})$", data).groups()) == 1
        return 'hash'
    except:
        pass

    try:
        len(re.match(r"^([a-zA-Z-\d\.]{2,})$", data).groups()) == 1
        return 'domain'
    except:
        pass

    return 'unknown'


class DNSBL_Base(object):
    def __init__(self):
        self.host = 'example.com'
        self.query_type = 'A'
        self.answer = None
        self.match = None
        self.result = None
        self.match_categories = []
        self.detailed_results = None
        self.category_info = None

    def do_query(self, query, query_type):
        try:
            answer = self.resolver.query(query, query_type)
        except dns.resolver.NXDOMAIN:
            answer = False
        return answer

    @staticmethod
    def reverse_ip(ip):
        rev = reversename.from_address(ip).to_text()
        if rev.endswith('.ip6.arpa.'):
            return rev[:-10]
        elif rev.endswith('.in-addr.arpa.'):
            return rev[:-14]
