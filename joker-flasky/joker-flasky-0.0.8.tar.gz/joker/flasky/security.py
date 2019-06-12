#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import hashlib
import time

from joker.cast import want_bytes, want_unicode


def _make_salt():
    return hex(int(time.time() * 65555))[-10:][::-1]


class HashedPassword(object):
    def __init__(self, digest, algo, salt):
        self.digest = digest
        self.algo = algo
        self.salt = salt

    @classmethod
    def parse(cls, s):
        digest, algo, salt = s.split(':')
        return cls(digest, algo, salt)

    @classmethod
    def generate(cls, password, algo='sha256', salt=None):
        if salt is None:
            salt = _make_salt()
        p = want_bytes(password)
        s = want_bytes(salt)
        h = hashlib.new(algo, p + s)
        return cls(h.hexdigest(), algo, want_unicode(salt))

    def __str__(self):
        return '{}:{}:{}'.format(self.digest, self.algo, self.salt)

    def verify(self, password):
        hp1 = self.generate(password, self.algo, self.salt)
        return self.digest == hp1.digest
