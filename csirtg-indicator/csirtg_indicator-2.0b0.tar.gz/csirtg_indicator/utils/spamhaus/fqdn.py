import arrow
from csirtg_indicator.utils.spamhaus import resolve_dbl as resolve


CODES = {
    '127.0.1.2': {
        'tags': 'suspicious',
        'description': 'spammed domain',
    },
    '127.0.1.3': {
        'tags': 'suspicious',
        'description': 'spammed redirector / url shortener',
    },
    '127.0.1.4': {
        'tags': 'phishing',
        'description': 'phishing domain',
    },
    '127.0.1.5': {
        'tags': 'malware',
        'description': 'malware domain',
    },
    '127.0.1.6': {
        'tags': 'botnet',
        'description': 'Botnet C&C domain',
    },
    '127.0.1.102': {
        'tags': 'suspicious',
        'description': 'abused legit spam',
    },
    '127.0.1.103': {
        'tags': 'suspicious',
        'description': 'abused legit spammed redirector',
    },
    '127.0.1.104': {
        'tags': 'phishing',
        'description': 'abused legit phish',
    },
    '127.0.1.105': {
        'tags': 'malware',
        'description': 'abused legit malware',
    },
    '127.0.1.106': {
        'tags': 'botnet',
        'description': 'abused legit botnet',
    },
    '127.0.1.255': {
        'description': 'BANNED',
    },
}


def process(i, confidence=4, resolve_geo=False):
    if not i.is_fqdn():
        return

    r = resolve(i.indicator)
    r = CODES.get(str(r), None)

    if not r:
        return

    if ' legit ' in r['description']:
        confidence = 1

    i2 = i.copy(**{
        'tags': r['tags'],
        'description': r['description'],
        'confidence': confidence,
        'provider': 'spamhaus.org',
        'reference': 'http://www.spamhaus.org/query/dbl?domain=%s' %
                     i.indicator,
        'reference_tlp': 'white',
        'last_at': arrow.utcnow(),
    })

    if resolve_geo:
        i2.geo_resolve()

    return i2


def main():
    from csirtg_indicator import Indicator
    i = Indicator('ns2.ndxylfpxuwowlhycfh.pw')
    import logging
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    print(process(i))


if __name__ == '__main__':
    main()
