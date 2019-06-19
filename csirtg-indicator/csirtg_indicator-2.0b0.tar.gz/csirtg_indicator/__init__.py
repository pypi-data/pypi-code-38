import json
import textwrap
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
from base64 import b64encode
import logging
import uuid
import copy
import arrow

from csirtg_indicator.constants import V4_RESERVED, PROTOCOL_VERSION, \
    FIELDS, FIELDS_TIME, LOG_FORMAT, VERSION, GEO, PEERS, FQDN, BASESTRING

from csirtg_indicator.utils import parse_timestamp, resolve_itype, \
    ipv4_normalize

from csirtg_indicator.wrappers.lookups import LookupMixin
from csirtg_indicator.wrappers.predict import PredictMixin
from csirtg_indicator.wrappers.formatter import FormatterMixin
from csirtg_indicator.wrappers.metadata import MetadataMixin
from csirtg_indicator.wrappers.itypes import ItypesMixin
from csirtg_indicator.wrappers.properties import PropertiesMixin


class Indicator(PropertiesMixin, LookupMixin, PredictMixin, FormatterMixin,
                MetadataMixin, ItypesMixin):

    def __init__(self, indicator=None, **kwargs):
        self.version = VERSION

        self._init_fields(**kwargs)

        if indicator:
            self.indicator = indicator

        # geo, fqdn, peers
        self._init_metadata(**kwargs)


    def _init_metadata(self, **kwargs):
        self.resolve_geo = kwargs.get('resolve_geo', GEO)
        self.resolve_peers = kwargs.get('resolve_peers', PEERS)
        self.resolve_fqdn = kwargs.get('resolve_fqdn', FQDN)

        if self.resolve_geo:
            self.geo_resolve()

        if self.resolve_peers:
            self.peers_resolve()

        if self.resolve_fqdn:
            self.fqdn_resolve()

    def _init_fields(self, **kwargs):
        for k in FIELDS:
            # handle these at the end
            if k in ['indicator', 'confidence', 'probability', 'count']:
                setattr(self, f"_{k}", None)
                continue

            if kwargs.get(k) is None:
                v = None

                setattr(self, k, v)
                continue

            # set this at the end
            if k in FIELDS_TIME:
                continue

            if isinstance(kwargs[k], BASESTRING):
                kwargs[k] = kwargs[k].lower()
                if k in ['tags', 'peers']:
                    kwargs[k] = kwargs[k].split(',')

            setattr(self, k, kwargs[k])

        for k in FIELDS_TIME:
            setattr(self, k, kwargs.get(k, None))
        
        self.confidence = kwargs.get('confidence', 0)
        self.count = kwargs.get('count', 1)
        self.probability = kwargs.get('probability', 0)
        self.uuid = kwargs.get('uuid', str(uuid.uuid4()))

    def copy(self, **kwargs):
        try:
            i = Indicator(**copy.deepcopy(self.__dict__()))

            for k in kwargs:
                setattr(i, k, kwargs[k])

            i.uuid = str(uuid.uuid4())
            if not isinstance(i.tags, list):
                i.tags = [i.tags]

            if not kwargs.get('last_at'):
                setattr(i, 'last_at', arrow.utcnow())

        except TypeError:
            i = None

        return i

    def format_keys(self):
        d = self.__dict__()
        for k in d:
            if not isinstance(d[k], str):
                continue

            if '{' not in d[k]:
                continue

            try:
                d[k] = d[k].format(**d)
            except (KeyError, ValueError, IndexError):
                pass

        return Indicator(**d)

    def __dict__(self):
        s = str(self)
        return json.loads(s)

    def __repr__(self):
        i = {}

        for k in FIELDS:

            v = getattr(self, k)
            if not v:
                continue

            if k == 'message':
                v = v.encode('utf-8')

                v = b64encode(v).decode('utf-8')

            if k in FIELDS_TIME and isinstance(v, datetime):
                v = v.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            if isinstance(v, BASESTRING) and k is not 'message' and \
                    not k.endswith('_at'):
                    v = v.lower()

            if k == 'confidence':
                v = float(v)

            i[k] = v

        sort_keys = False
        indent = None
        if logging.getLogger('').getEffectiveLevel() == logging.DEBUG:
            sort_keys = True
            indent = 4
        try:
            return json.dumps(i, indent=indent, sort_keys=sort_keys,
                              separators=(',', ': '))

        except UnicodeDecodeError as e:
            i['asn_desc'] = unicode(i['asn_desc'].decode('latin-1'))
            return json.dumps(i, indent=indent, sort_keys=sort_keys,
                              separators=(',', ': '))

    def __eq__(self, other):
        d1 = self.__dict__()
        d2 = other.__dict__()
        return d1 == d2


def main():
    p = ArgumentParser(
        description=textwrap.dedent('''\
             Env Variables:
                CSIRTG_INDICATOR_TLP
                CSIRTG_INDICATOR_GROUP

            example usage:
                $ csirtg-indicator -d
            '''),
        formatter_class=RawDescriptionHelpFormatter,
        prog='csirtg-indicator'
    )

    p.add_argument('-d', '--debug', dest='debug', action="store_true")
    p.add_argument('-V', '--version', action='version', version=VERSION)

    p.add_argument('--group', help="specify group")
    p.add_argument('--indicator', '-i', help="specify indicator")
    p.add_argument('--tlp', help='specify tlp', default='green')
    p.add_argument('--tags', help='specify tags')

    args = p.parse_args()

    loglevel = logging.getLevelName('INFO')

    if args.debug:
        loglevel = logging.DEBUG

    console = logging.StreamHandler()
    logging.getLogger('').setLevel(loglevel)
    console.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger('').addHandler(console)

    i = Indicator(indicator=args.indicator, tlp=args.tlp, tags=args.tags)

    print(i)


if __name__ == '__main__':
    main()
