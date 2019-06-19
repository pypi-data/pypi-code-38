import os
import pytricia

from .patterns import *
from .fields import FIELDS, FIELDS_TIME
from .networks import V4_RESERVED, V6_RESERVED

from csirtg_indicator._version import get_versions
__version__ = get_versions()['version']
VERSION = __version__
del get_versions

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s[%(lineno)s] - %(message)s'
PROTOCOL_VERSION = '2.0.0-a.1'

COLUMNS = ['tlp', 'group', 'reported_at', 'indicator', 'asn', 'cc', 'first_at',
           'last_at', 'count', 'tags', 'description', 'confidence', 'rdata',
           'provider', 'probability', 'reference']

MAX_FIELD_SIZE = 30

BASESTRING = (str, bytes)

GEO = os.getenv('CSIRTG_INDICATOR_GEO', False)
if GEO == '1':
    GEO = True

PEERS = os.getenv('CSIRTG_INDICATOR_PEERS', False)
if PEERS == '1':
    PEERS = True

FQDN = os.getenv('CSIRTG_INDICATOR_FQDN', False)
if FQDN == '1':
    FQDN = True
