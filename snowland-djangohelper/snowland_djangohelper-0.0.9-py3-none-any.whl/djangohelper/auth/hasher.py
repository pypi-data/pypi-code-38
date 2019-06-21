#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: hasher.py
# @time: 2018/11/15 17:03
# @Software: PyCharm

import base64
import binascii
from collections import OrderedDict

import pysmx
from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import (
    constant_time_compare, )
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import gettext_noop as _

from djangohelper.utils.crypto import pbkdf2


class SM3PasswordHasher(BasePasswordHasher):
    algorithm = 'sm3'
    library = ('SM3', 'pysmx.SM3')

    def encode(self, password, salt):
        assert password is not None
        assert salt and '$' not in salt
        SM3 = self._load_library()
        hash = SM3.Hash_sm3(force_bytes(salt + password))
        return "%s$%s$%s" % (self.algorithm, salt, hash)

    def verify(self, password, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt)
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('salt'), mask_hash(salt, show=2)),
            (_('hash'), mask_hash(hash)),
        ])


class UnsaltedSM3PasswordHasher(BasePasswordHasher):
    """
    Very insecure algorithm that you should *never* use; store SM3 hashes
    with an empty salt.

    This class is implemented because Django used to accept such password
    hashes. Some older Django installs still have these values lingering
    around so we need to handle and upgrade them properly.
    """
    algorithm = "unsalted_sm3"
    library = ('SM3', 'pysmx.SM3')

    def salt(self):
        return ''

    def encode(self, password, salt):
        assert salt == ''
        SM3 = self._load_library()
        hash = SM3.digest(force_bytes(password))
        return 'sm3$$%s' % hash

    def verify(self, password, encoded):
        encoded_2 = self.encode(password, '')
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        assert encoded.startswith('sm3$$')
        hash = encoded[6:]
        return OrderedDict([
            (_('algorithm'), self.algorithm),
            (_('hash'), mask_hash(hash)),
        ])

    def harden_runtime(self, password, encoded):
        pass


class PBKDF2_SM3PasswordHasher(BasePasswordHasher):
    algorithm = "pbkdf2_sm3"
    iterations = 100000
    library = ('SM3', 'pysmx.SM3')

    def encode(self, password, salt, iterations=None):
        assert password is not None
        assert salt and '$' not in salt
        SM3 = self._load_library()
        if not iterations:
            iterations = self.iterations
        hash = pbkdf2(password, salt, iterations, digest=SM3)
        hash = base64.b64encode(hash).decode('ascii').strip()
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, hash)

    def verify(self, password, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt, int(iterations))
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('iterations'), iterations),
            (_('salt'), mask_hash(salt)),
            (_('hash'), mask_hash(hash)),
        ])

    def must_update(self, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        return int(iterations) != self.iterations

    def harden_runtime(self, password, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        extra_iterations = self.iterations - int(iterations)
        if extra_iterations > 0:
            self.encode(password, salt, extra_iterations)


class BCryptSM3PasswordHasher(BasePasswordHasher):
    """
    Secure password hashing using the bcrypt algorithm (recommended)

    This is considered by many to be the most secure algorithm but you
    must first install the bcrypt library.  Please be warned that
    this library depends on native C code and might cause portability
    issues.
    """
    algorithm = "bcrypt_sm3"
    digest = pysmx.SM3
    library = ("bcrypt", "bcrypt")
    rounds = 12

    def salt(self):
        bcrypt = self._load_library()
        return bcrypt.gensalt(self.rounds)

    def encode(self, password, salt):
        bcrypt = self._load_library()
        # Hash the password prior to using bcrypt to prevent password
        # truncation as described in #20138.
        if self.digest is not None:
            # Use binascii.hexlify() because a hex encoded bytestring is str.
            password = binascii.hexlify(self.digest.digest(force_bytes(password)))
        else:
            password = force_bytes(password)

        data = bcrypt.hashpw(password, salt)
        return "%s$%s" % (self.algorithm, force_text(data))

    def verify(self, password, encoded):
        algorithm, data = encoded.split('$', 1)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, force_bytes(data))
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, empty, algostr, work_factor, data = encoded.split('$', 4)
        assert algorithm == self.algorithm
        salt, checksum = data[:22], data[22:]
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('work factor'), work_factor),
            (_('salt'), mask_hash(salt)),
            (_('checksum'), mask_hash(checksum)),
        ])

    def must_update(self, encoded):
        algorithm, empty, algostr, rounds, data = encoded.split('$', 4)
        return int(rounds) != self.rounds

    def harden_runtime(self, password, encoded):
        _, data = encoded.split('$', 1)
        salt = data[:29]  # Length of the salt in bcrypt.
        rounds = data.split('$')[2]
        # work factor is logarithmic, adding one doubles the load.
        diff = 2 ** (self.rounds - int(rounds)) - 1
        while diff > 0:
            self.encode(password, force_bytes(salt))
            diff -= 1


class SM3KDFPasswordHasher(BasePasswordHasher):
    """
        Very insecure algorithm that you should *never* use; store SM3 hashes
        with an empty salt.

        This class is implemented because Django used to accept such password
        hashes. Some older Django installs still have these values lingering
        around so we need to handle and upgrade them properly.
        """
    algorithm = "sm3kdf"
    iterations = 100000
    library = ('SM3', 'pysmx.SM3')

    def salt(self):
        return ''

    def encode(self, password, salt, iterations=None):
        assert salt == ''
        if not iterations:
            iterations = self.iterations
        SM3 = self._load_library()
        if isinstance(password, 'str'):
            hash = SM3.KDF(password, self.iterations)
        elif isinstance(password, (bytes, bytearray)):
            hash = SM3.KDF(str(password, encoding='utf-8'), self.iterations)
        else:
            raise ValueError("password error")
        return 'sm3kdf$%d$$%s' % (iterations, hash)

    def verify(self, password, encoded):
        encoded_2 = self.encode(password, '')
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded, iterations=None):
        assert encoded.startswith('sm3kdf$')
        if iterations is None:
            iterations = self.iterations
        hash = encoded.splite('$')[-1]
        return OrderedDict([
            (_('algorithm'), self.algorithm),
            (_('iterations'), iterations),
            (_('hash'), mask_hash(hash)),
        ])

    def harden_runtime(self, password, encoded):
        pass
