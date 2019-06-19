
import pytricia
from csirtg_indicator.utils.network import is_valid_ip

from pprint import pprint

PERM_WHITELIST = [
    "0.0.0.0/8",
    "10.0.0.0/8",
    "127.0.0.0/8",
    "192.168.0.0/16",
    "169.254.0.0/16",
    "192.0.2.0/24",
    "224.0.0.0/4",
    "240.0.0.0/5",
    "248.0.0.0/5",
]

LARGEST_PREFIX = '8'


def _normalize(i):
    bits = i.split('.')

    rv = []
    for b in bits:
        if len(b) > 1 and b.startswith('0') and not b.startswith('0/'):
            b = b[1:]
        rv.append(b)

    i = '.'.join(rv)

    return i


# https://github.com/jsommers/pytricia
def process(data=[], whitelist=[]):
    wl = pytricia.PyTricia()
    for x in PERM_WHITELIST:
        wl[x] = True

    for y in whitelist:
        y = str(_normalize(y['indicator']))
        # weird bug work-around it'll insert 172.16.1.60 with a /0 at the end??
        if '/' not in y:
            y = '{}/32'.format(y)

        wl[y] = True

    for i in data:
        if 'whitelist' in set(i['tags']):
            continue

        i['indicator'] = _normalize(i['indicator'])

        if not is_valid_ip(i['indicator']):
            continue

        if str(i['indicator']) not in wl:
            yield i
