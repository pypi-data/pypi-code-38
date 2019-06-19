import socket
import dns.resolver
from dns.resolver import NoAnswer, NXDOMAIN, NoNameservers, Timeout
from dns.name import EmptyLabel
import re
import ipaddress

TIMEOUT = 5


try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def resolve_fqdn(host):
    if not host:
        return

    try:
        host = socket.gethostbyname(host)
        return host
    except Exception as e:
        return


def resolve_url(url):
    u = urlparse(url)
    return u.hostname


def resolve_ns(data, t='A', timeout=TIMEOUT, nameserver=None):
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout
    resolver.search = []

    if nameserver:
        resolver.nameservers = [nameserver]

    try:
        answers = resolver.query(data, t)

    except (NoAnswer, NXDOMAIN, EmptyLabel, NoNameservers, Timeout) as e:
        e = str(e)
        if e.startswith('The DNS operation timed out after'):
            return

        if 'The DNS response does not contain' in e or \
                'None of DNS query names exist' in e:
            return

        raise

    resp = []
    for rdata in answers:
        resp.append(rdata)

    return resp


def resolve_peers(indicator):
    if indicator.is_private() or not indicator.itype == 'ipv4':
        return indicator

    i = str(indicator.indicator)
    match = re.search('^(\S+)\/\d+$', i)
    if match:
        i = match.group(1)

    # cache it to the /24
    i = list(reversed(i.split('.')))
    i = '0.{}.{}.{}'.format(i[1], i[2], i[3])

    answers = resolve_ns('{}.{}'.format(i, 'peer.asn.cymru.com', timeout=15),
                         t='TXT')

    if answers is None or len(answers) == 0:
        return indicator

    if not indicator.peers:
        indicator.peers = []

    # Separate fields and order by netmask length
    # 23028 | 216.90.108.0/24 | US | arin | 1998-09-25
    # 701 1239 3549 3561 7132 | 216.90.108.0/24 | US | arin | 1998-09-25
    for p in answers:
        bits = str(p).replace('"', '').strip().split(' | ')
        asn = bits[0]
        prefix = bits[1]
        cc = bits[2]
        rir = bits[3]
        asns = asn.split(' ')
        for a in asns:
            indicator.peers.append({
                'asn': a,
                'prefix': prefix,
                'cc': cc,
                'rir': rir
            })

    return indicator


def is_valid_ip(i):
    try:
        ipaddress.ip_network(i)
        return True
    except ValueError as e:
        return False
