import os
import sys

from netaddr import IPRange, IPSet
from netaddr.core import AddrFormatError


def get_ip_set(subnet):
    try:
        return IPSet([subnet])
    except AddrFormatError:
        try:
            start, end = subnet.split('-')
            return IPSet(IPRange(start, end))
        except (AddrFormatError, ValueError):
            print(u'error: invalid subnet format {}'.format(subnet))
            sys.exit(1)


def parse_subnet_file(path):
    subnets = []
    if os.path.isfile(path):
        lines = open(path).read().splitlines()
        for line in lines:
            line = line.strip()
            if not line.startswith('#'):
                subnets.append(line)
        return subnets
    else:
        print(u'warning: invalid subnets file')
        return []


def check_conflicts(subnets):
    conflicts = []
    for idx, subnet_a in enumerate(subnets):
        for subnet_b in subnets[idx+1:]:
            overlapping_ips = get_ip_set(subnet_a) & get_ip_set(subnet_b)
            if overlapping_ips:
                conflicts.append((subnet_a, subnet_b, overlapping_ips))
    return conflicts
