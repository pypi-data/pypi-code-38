from csirtg_indicator.utils.network import resolve_ns
import os

NAMESERVER = os.getenv('CSIRTG_INDICATOR_NAMESERVER', '1.1.1.1')


def _resolve(data, s):
    data = '%s.%s.spamhaus.org' % (data, s)
    data = resolve_ns(data, nameserver=NAMESERVER)
    if data and data[0]:
        return data[0]


def resolve_dbl(data):
    return _resolve(data, 'dbl')


def resolve_zen(data):
    data = '.'.join(reversed(data.split('.')))
    return _resolve(data, 'zen')
