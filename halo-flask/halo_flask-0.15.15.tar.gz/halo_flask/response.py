from __future__ import print_function

import logging
from halo_flask.classes import AbsBaseClass
logger = logging.getLogger(__name__)


class HaloResponse(AbsBaseClass):

    payload = 'this is HaloResponse'
    code = 200
    headers = []

    def __init__(self, payload=None, code=None, headers=None):
        if payload:
            self.payload = payload
        if code:
            self.code = code
        if headers:
            self.headers = headers
