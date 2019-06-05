""" Web-related utilities """

import sys
if sys.version_info < (3, 0):
    from urlparse import urlparse
else:
    from urllib.parse import urlparse


__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["is_url"]


def is_url(maybe_url):
    """
    Determine whether a path is a URL.

    :param str maybe_url: path to investigate as URL
    :return bool: whether path appears to be a URL
    """
    return urlparse(maybe_url).scheme != ""
