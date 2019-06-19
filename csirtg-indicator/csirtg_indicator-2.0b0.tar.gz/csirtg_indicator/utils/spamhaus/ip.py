from csirtg_indicator.utils.spamhaus import resolve_zen as resolve

from pprint import pprint
import arrow

CODES = {
    '127.0.0.2': {
        'tags': 'spam',
        'description': 'Direct UBE sources, spam operations & spam services',
    },
    '127.0.0.3': {
        'tags': 'spam',
        'description': 'Direct snowshoe spam sources detected via automation',
    },
    '127.0.0.4': {
        'tags': ['exploit', 'malware'],
        'description': 'CBL + customised NJABL. 3rd party exploits (proxies, '
                       'trojans, etc.)',
    },
    '127.0.0.5': {
        'tags': ['exploit', 'malware'],
        'description': 'CBL + customised NJABL. 3rd party exploits (proxies, '
                       'trojans, etc.)',
    },
    '127.0.0.6': {
        'tags': ['exploit', 'malware'],
        'description': 'CBL + customised NJABL. 3rd party exploits (proxies, '
                       'trojans, etc.)',
    },
    '127.0.0.7': {
        'tags': ['exploit', 'malware'],
        'description': 'CBL + customised NJABL. 3rd party exploits (proxies, '
                       'trojans, etc.)',
    },
    '127.0.0.9': {
        'tags': 'hijacked',
        'description': 'Spamhaus DROP/EDROP Data',
    },
}


def process(i, confidence=4, resolve_geo=False):
    if not i.is_ip():
        return

    r = resolve(i.indicator)
    r = CODES.get(str(r), None)

    if not r:
        return

    i2 = i.copy(**{
        'tags': r['tags'],
        'description': r['description'],
        'confidence': confidence,
        'provider': 'spamhaus.org',
        'reference': 'http://www.spamhaus.org/query/bl?ip=%s' % i.indicator,
        'reference_tlp': 'white',
        'last_at': arrow.utcnow(),
    })

    if resolve_geo:
        i2.geo_resolve()

    return i2


def main():
    from csirtg_indicator import Indicator
    i = Indicator('71.6.146.130')
    import logging
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    print(process(i))


if __name__ == '__main__':
    main()
