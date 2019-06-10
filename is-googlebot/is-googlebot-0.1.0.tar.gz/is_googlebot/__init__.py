import re
import socket
import user_agents
from functools import lru_cache


__all__ = 'is_googlebot', 'gethostbyaddr', 'gethostbyname', 'test',
googlebot_re = re.compile(r'''(^|\b)(google|googlebot)($|\b)''', re.I)
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


def is_googlebot(ip_address, user_agent):
    ua = user_agents.parse(user_agent)

    if ua.is_bot is False or not googlebot_re.search(ua.browser.family):
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

    return gethostbyname(host) == ip


test = is_googlebot
