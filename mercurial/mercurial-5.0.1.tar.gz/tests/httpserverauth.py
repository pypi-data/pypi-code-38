from __future__ import absolute_import

import base64
import hashlib

from mercurial.hgweb import common
from mercurial import (
    node,
)

def parse_keqv_list(req, l):
    """Parse list of key=value strings where keys are not duplicated."""
    parsed = {}
    for elt in l:
        k, v = elt.split(b'=', 1)
        if v[0:1] == b'"' and v[-1:] == b'"':
            v = v[1:-1]
        parsed[k] = v
    return parsed

class digestauthserver(object):
    def __init__(self):
        self._user_hashes = {}

    def gethashers(self):
        def _md5sum(x):
            m = hashlib.md5()
            m.update(x)
            return node.hex(m.digest())

        h = _md5sum

        kd = lambda s, d, h=h: h(b"%s:%s" % (s, d))
        return h, kd

    def adduser(self, user, password, realm):
        h, kd = self.gethashers()
        a1 = h(b'%s:%s:%s' % (user, realm, password))
        self._user_hashes[(user, realm)] = a1

    def makechallenge(self, realm):
        # We aren't testing the protocol here, just that the bytes make the
        # proper round trip.  So hardcoded seems fine.
        nonce = b'064af982c5b571cea6450d8eda91c20d'
        return b'realm="%s", nonce="%s", algorithm=MD5, qop="auth"' % (realm,
                                                                       nonce)

    def checkauth(self, req, header):
        log = req.rawenv[b'wsgi.errors']

        h, kd = self.gethashers()
        resp = parse_keqv_list(req, header.split(b', '))

        if resp.get(b'algorithm', b'MD5').upper() != b'MD5':
            log.write(b'Unsupported algorithm: %s' % resp.get(b'algorithm'))
            raise common.ErrorResponse(common.HTTP_FORBIDDEN,
                                       b"unknown algorithm")
        user = resp[b'username']
        realm = resp[b'realm']
        nonce = resp[b'nonce']

        ha1 = self._user_hashes.get((user, realm))
        if not ha1:
            log.write(b'No hash found for user/realm "%s/%s"' % (user, realm))
            raise common.ErrorResponse(common.HTTP_FORBIDDEN, b"bad user")

        qop = resp.get(b'qop', b'auth')
        if qop != b'auth':
            log.write(b"Unsupported qop: %s" % qop)
            raise common.ErrorResponse(common.HTTP_FORBIDDEN, b"bad qop")

        cnonce, ncvalue = resp.get(b'cnonce'), resp.get(b'nc')
        if not cnonce or not ncvalue:
            log.write(b'No cnonce (%s) or ncvalue (%s)' % (cnonce, ncvalue))
            raise common.ErrorResponse(common.HTTP_FORBIDDEN, b"no cnonce")

        a2 = b'%s:%s' % (req.method, resp[b'uri'])
        noncebit = b"%s:%s:%s:%s:%s" % (nonce, ncvalue, cnonce, qop, h(a2))

        respdig = kd(ha1, noncebit)
        if respdig != resp[b'response']:
            log.write(b'User/realm "%s/%s" gave %s, but expected %s'
                      % (user, realm, resp[b'response'], respdig))
            return False

        return True

digest = digestauthserver()

def perform_authentication(hgweb, req, op):
    auth = req.headers.get(b'Authorization')

    if req.headers.get(b'X-HgTest-AuthType') == b'Digest':
        if not auth:
            challenge = digest.makechallenge(b'mercurial')
            raise common.ErrorResponse(common.HTTP_UNAUTHORIZED, b'who',
                    [(b'WWW-Authenticate', b'Digest %s' % challenge)])

        if not digest.checkauth(req, auth[7:]):
            raise common.ErrorResponse(common.HTTP_FORBIDDEN, b'no')

        return

    if not auth:
        raise common.ErrorResponse(common.HTTP_UNAUTHORIZED, b'who',
                [(b'WWW-Authenticate', b'Basic Realm="mercurial"')])

    if base64.b64decode(auth.split()[1]).split(b':', 1) != [b'user', b'pass']:
        raise common.ErrorResponse(common.HTTP_FORBIDDEN, b'no')

def extsetup(ui):
    common.permhooks.insert(0, perform_authentication)
    digest.adduser(b'user', b'pass', b'mercurial')
