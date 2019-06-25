from ._version import get_versions
VERSION = get_versions()['version']
del get_versions

import os.path
import tempfile
import sys
from csirtg_indicator.constants import COLUMNS

PYVERSION = 2
if sys.version_info > (3,):
    PYVERSION = 3

TEMP_DIR = os.path.join(tempfile.gettempdir())
RUNTIME_PATH = os.getenv('CIF_RUNTIME_PATH', TEMP_DIR)
DATA_PATH = os.getenv('CIF_DATA_PATH', TEMP_DIR)


# Logging stuff
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s[%(lineno)s][%(threadName)s] - %(message)s'

LOGLEVEL = 'ERROR'
LOGLEVEL = os.getenv('CIF_LOGLEVEL', LOGLEVEL).upper()

CONFIG_PATH = os.getenv('CIF_CONFIG_PATH', os.path.join(os.getcwd(), 'cif.yml'))
if not os.path.isfile(CONFIG_PATH):
    CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.cif.yml')

# address stuff

REMOTE_ADDR = 'http://localhost:5000'
REMOTE_ADDR = os.getenv('CIF_REMOTE', REMOTE_ADDR)

ROUTER_ADDR = "ipc://{}".format(os.path.join(RUNTIME_PATH, 'router.ipc'))
ROUTER_ADDR = os.getenv('CIF_ROUTER_ADDR', ROUTER_ADDR)

SEARCH_LIMIT = os.getenv('CIF_SEARCH_LIMIT', 500)

TOKEN = os.getenv('CIF_TOKEN', None)
FORMAT = os.getenv('CIF_FORMAT', 'table')

ADVANCED = os.getenv('CIF_ADVANCED', False)
if ADVANCED == '1':
    ADVANCED = True
else:
    ADVANCED = False

COLUMNS = os.getenv('CIFSDK_COLUMNS', COLUMNS)
if not isinstance(COLUMNS, list):
    COLUMNS = COLUMNS.split(',')


MAX_FIELD_SIZE = 30

VALID_FILTERS = ['indicator', 'itype', 'confidence', 'provider', 'limit', 'application', 'nolog', 'tags', 'days',
                 'hours', 'groups', 'reported_at', 'cc', 'asn', 'asn_desc', 'rdata', 'first_at', 'last_at', 'region',
                 'probability', 'no_feed', 'days', 'hours', 'today', 'latitude', 'longitude', 'probability']

PROFILES = {
    'splunk': {
        'format': 'csv',
        'confidence': 3,
        'hours': 1,
        'limit': 25000,
        'itype': 'ipv4',
    },
    'bind': {
        'format': 'bind',
        'confidence': 4,
        'itype': 'fqdn',
        'days': 45,
        'tags': 'phishing,malware,botnet',
        'limit': 250000,
    },
    'bro': {
        'confidence': 3,
        'format': 'bro',
        'itype': 'ipv4',
        'days': 21,
        'limit': 250000,
        'tags': 'botnet'
    },
    'snort': {
        'confidence': 3,
        'itype': 'ipv4',
        'format': 'snort',
        'days': 21,
        'limit': 250000,
        'tags': 'botnet'
    },
    'firewall': {
        'format': 'csv',
        'itype': 'ipv4',
        'confidence': 4,
        'days': 21,
        'tags': 'scanner,bruteforce,botnet',
        'limit': 25000,
    },
    'sem': {
        'format': 'csv',
        'confidence': 3,
        'hours': 1,
        'limit': 25000,
        'itype': 'ipv4',
    },
}