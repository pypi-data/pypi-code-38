#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2016  Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016  Adrien Cossa (souliane@mailoo.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


""" Tests for the plugin radiocol """

from sat.test import helpers
from sat.memory.crypto import BlockCipher, PasswordHasher
import random
import string
from twisted.internet import defer


def getRandomUnicode(len):
    """Return a random unicode string"""
    return u"".join(random.choice(string.letters + u"éáúóâêûôßüöä") for i in xrange(len))


class CryptoTest(helpers.SatTestCase):
    def setUp(self):
        self.host = helpers.FakeSAT()

    def test_encrypt_decrypt(self):
        d_list = []

        def test(key, message):
            d = BlockCipher.encrypt(key, message)
            d.addCallback(lambda ciphertext: BlockCipher.decrypt(key, ciphertext))
            d.addCallback(lambda decrypted: self.assertEqual(message, decrypted))
            d_list.append(d)

        for key_len in (0, 2, 8, 10, 16, 24, 30, 32, 40):
            key = getRandomUnicode(key_len)
            for message_len in (0, 2, 16, 24, 32, 100):
                message = getRandomUnicode(message_len)
                test(key, message)
        return defer.DeferredList(d_list)

    def test_hash_verify(self):
        d_list = []
        for password in (0, 2, 8, 10, 16, 24, 30, 32, 40):
            d = PasswordHasher.hash(password)

            def cb(hashed):
                d1 = PasswordHasher.verify(password, hashed)
                d1.addCallback(lambda result: self.assertTrue(result))
                d_list.append(d1)
                attempt = getRandomUnicode(10)
                d2 = PasswordHasher.verify(attempt, hashed)
                d2.addCallback(lambda result: self.assertFalse(result))
                d_list.append(d2)

            d.addCallback(cb)
        return defer.DeferredList(d_list)
