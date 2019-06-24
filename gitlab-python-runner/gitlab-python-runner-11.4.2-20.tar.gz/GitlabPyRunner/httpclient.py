"""
OO Wrapper around requests
"""
import sys
import requests

from . import consts


class Session(requests.Session):
    """
    A HTTP user agent complete with cookies
    """
    def __init__(self):
        super(Session, self).__init__()
        pyver = sys.version_info
        pyver_str = "; python {}.{}".format(pyver.major, pyver.minor)
        self.headers["User-Agent"] = consts.USER_AGENT + " " + pyver_str
