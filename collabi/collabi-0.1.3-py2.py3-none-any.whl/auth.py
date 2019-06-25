"""Provides authentication callback for requests.
"""

from requests.auth import AuthBase

class Auth(AuthBase):
    def __init__(self, authorizor):
        self._authorizor = authorizor
        super(Auth, self).__init__()

    def __call__(self, req):
        req.headers['Authorization'] = self._authorizor.get_authorization_header()
        return req
