"""
Utility functions used provided by the logging_toolbox module.
"""
from six.moves.urllib.parse import urlparse, urlunparse


def clean_url(url):
    """
    Returns a sanitized (password blocked) version of the url.

    :param str url: The URL to be sanitized.
    :rtype: str
    """
    parsed = urlparse(url)
    if parsed.username is not None and parsed.password is not None:
        creds = '{}:******'.format(parsed.username)
        netloc = '{}@{}'.format(creds, parsed.hostname)
        if parsed.port is not None:
            netloc = '{}:{}'.format(netloc, parsed.port)
        return urlunparse(parsed._replace(netloc=netloc))
    return url
