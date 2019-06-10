import re
import socket
from functools import lru_cache


# __all__ = 'is_googlebot', 'gethostbyaddr', 'gethostbyname', 'test',
GOOGLEBOT_RE = re.compile(r'''\b(google|googlebot)\b''', re.I)
GOOGLEBOT_DOMAINS = {'googlebot', 'google'}


@lru_cache(4096)
def gethostbyaddr(ip_address):
    try:
        return socket.gethostbyaddr(ip_address)[0]
    except (socket.herror, socket.error):
        return False


@lru_cache(4096)
def gethostbyname(hostname):
    return socket.gethostbyname(hostname)


def is_googlebot(ip_address, user_agent=None):
    if user_agent is not None and not GOOGLEBOT_RE.search(user_agent):
        return False

    host = gethostbyaddr(ip_address)
    if host is False:
        return False

    host_parts = host.split('.')
    try:
        if host_parts[-1] != 'com' or host_parts[-2] not in GOOGLEBOT_DOMAINS:
            return False
    except IndexErro:
        return False

    return gethostbyname(host) == ip_address


test = is_googlebot
