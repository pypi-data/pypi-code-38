"""A collection of constants for use elsewhere."""


import os
import sys


#
#   File and Directory
#

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, 'settings.ini')


#
#   Platform and Version
#

PLATFORM = sys.platform.lower()
LINUX = PLATFORM.startswith('lin')
WINDOWS = PLATFORM.startswith('win')

PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3


#
#   Time
#

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24


#
#   Request Headers
#

HEADER_ACCEPT_KEY = 'Accept'
HEADER_ACCEPT_TEXT_HTML = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

HEADER_ACCEPT_ENCODING_KEY = 'Accept-Encoding'
HEADER_ACCEPT_ENCODING_GZIP_DEFLATED = 'gzip, deflate'

HEADER_ACCEPT_LANGUAGE_KEY = 'Accept-Language'
HEADER_ACCEPT_LANGUAGE_ENGLISH = 'en-US,en;q=0.5'

HEADER_CACHE_CONTROL_KEY = 'Cache-Control'
HEADER_CACHE_CONTROL_NONE = 'max-age=0'

HEADER_CONNECTION_KEY = 'Connection'
HEADER_CONNECTION_KEEP_ALIVE = 'keep-alive'

HEADER_USER_AGENT_KEY = 'User-Agent'
HEADER_USER_AGENT_PALEMOON_27_4_1 = (
    'Mozilla/5.0 (X11; Linux x86_64; rv:45.9) Gecko/20100101 Goanna/3.2 Firefox/45.9 PaleMoon/27.4.1'
)
HEADER_USER_AGENT_PALEMOON_28_3_0 = (
    'Mozilla/5.0 (X11; Linux x86_64; rv:60.9) Gecko/20100101 Goanna/4.1 Firefox/60.9 PaleMoon/28.3.0'
)


# these are held in a list in case order makes the user agent look less suspicious
HEADER_DEFAULTS = [
    (HEADER_USER_AGENT_KEY, HEADER_USER_AGENT_PALEMOON_28_3_0),
    (HEADER_ACCEPT_KEY, HEADER_ACCEPT_TEXT_HTML),
    (HEADER_ACCEPT_LANGUAGE_KEY, HEADER_ACCEPT_LANGUAGE_ENGLISH),
    (HEADER_ACCEPT_ENCODING_KEY, HEADER_ACCEPT_ENCODING_GZIP_DEFLATED),
    (HEADER_CACHE_CONTROL_KEY, HEADER_CACHE_CONTROL_NONE)
]


#
#   Strings
#

EMPTY_DICT_SHA256_HEXDIGEST = '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a'
EMPTY_STRING_SHA256_HEXDIGEST = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

UTF_16 = 'utf-16'
UTF_16_LE = 'utf-16-le'
UTF_8 = 'utf-8'
