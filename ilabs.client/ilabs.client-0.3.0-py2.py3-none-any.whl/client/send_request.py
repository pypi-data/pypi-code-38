from __future__ import absolute_import, unicode_literals

import logging
import sys
from ilabs.client import __version__


try:
    from urllib2 import Request, urlopen, HTTPError
    from urllib import urlencode
except ImportError:
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
    from urllib.error import HTTPError


ILABS_USER_AGENT = 'ILabs API client ' + __version__


def send_request(method, url, data=None, headers=None, query=None):
    logging.debug('%s %s %s', method, url, query)
    assert method in ('GET', 'POST', 'DELETE')
    if data is not None:
        assert method == 'POST'
    else:
        assert method in ('GET', 'POST', 'DELETE')

    if query is not None:
        url = url + '?' + urlencode(query)
        logging.debug('url with query string encoded: %s', url)

    # ugly!
    if sys.version_info[0] < 3:
        url = url.encode()
        if headers is not None:
            headers = {
                key.encode(): val.encode()
                for key, val in headers.items()
            }

    return urlopen(Request(url, headers=headers, data=data))
