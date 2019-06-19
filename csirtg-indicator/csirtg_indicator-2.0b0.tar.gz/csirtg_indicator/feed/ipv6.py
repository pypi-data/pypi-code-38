import pytricia
from csirtg_indicator.utils.network import is_valid_ip

PERM_WHITELIST = [
    # TODO -- more
    # http://www.iana.org/assignments/ipv6-multicast-addresses/ipv6-multicast-addresses.xhtml
    # v6
    'FF01:0:0:0:0:0:0:1',
    'FF01:0:0:0:0:0:0:2',
]


def process(data, whitelist=[]):
    wl = pytricia.PyTricia()

    [wl.insert(x, True) for x in PERM_WHITELIST]

    [wl.insert(str(y['indicator']), True) for y in whitelist]

    for i in data:
        if 'whitelist' in set(i['tags']):
            continue

        if not is_valid_ip(i['indicator']):
            continue

        if str(i['indicator']) not in wl:
            yield i
