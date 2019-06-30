"""
Network related utilities
"""

import json
import socket
import urllib.parse
import urllib.request

REMOTE_SERVER = "www.google.com"

def isConnected(hostname=None):
    """
    Convenience function to test for web server connection
    no parameters checks for internet connection

    Args:
        hostname (str): hostname to test for connection
    """

    if hostname is None:
        hostname = REMOTE_SERVER

    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(hostname)

        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        s.close()

        return True

    except OSError:

        pass

    return False


def urlSearchJson(url, data=None, headers=None):
    """
    url request to a site that returns json data

    Args:
        url (str): URL for request
        data (:obj:`dict`, optional): dictionary with data for GET
        headers (:obj:`dict`, optional): dictionary with any needed headers

    Returns:
        dict:

        dictionary with the json response
    """

    if data is not None:
        request = urllib.request.Request(url, data=data)
    else:
        request = urllib.request.Request(url)

    if headers is not None:
        for key in headers:
            request.add_header(key, headers[key])

    result = urllib.request.urlopen(request)

    if result.status == 200:

        bJson = result.read()
        data = json.loads(bJson.decode('utf-8'))
        return data

    return None
