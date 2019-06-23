#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

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

try:
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2
except ImportError:
    raise Exception("PyCrypto is not installed.")

from os import urandom
from base64 import b64encode, b64decode
from twisted.internet.threads import deferToThread
from twisted.internet.defer import succeed


class BlockCipher(object):

    BLOCK_SIZE = AES.block_size  # 16 bits
    MAX_KEY_SIZE = AES.key_size[-1]  # 32 bits = AES-256
    IV_SIZE = BLOCK_SIZE  # initialization vector size, 16 bits

    @classmethod
    def encrypt(cls, key, text, leave_empty=True):
        """Encrypt a message.

        Based on http://stackoverflow.com/a/12525165

        @param key (unicode): the encryption key
        @param text (unicode): the text to encrypt
        @param leave_empty (bool): if True, empty text will be returned "as is"
        @return: Deferred: base-64 encoded str
        """
        if leave_empty and text == "":
            return succeed(text)
        iv = BlockCipher.getRandomKey()
        key = key.encode("utf-8")
        key = (
            key[: BlockCipher.MAX_KEY_SIZE]
            if len(key) >= BlockCipher.MAX_KEY_SIZE
            else BlockCipher.pad(key)
        )
        cipher = AES.new(key, AES.MODE_CFB, iv)
        d = deferToThread(cipher.encrypt, BlockCipher.pad(text.encode("utf-8")))
        d.addCallback(lambda ciphertext: b64encode(iv + ciphertext))
        return d

    @classmethod
    def decrypt(cls, key, ciphertext, leave_empty=True):
        """Decrypt a message.

        Based on http://stackoverflow.com/a/12525165

        @param key (unicode): the decryption key
        @param ciphertext (base-64 encoded str): the text to decrypt
        @param leave_empty (bool): if True, empty ciphertext will be returned "as is"
        @return: Deferred: str or None if the password could not be decrypted
        """
        if leave_empty and ciphertext == "":
            return succeed("")
        ciphertext = b64decode(ciphertext)
        iv, ciphertext = (
            ciphertext[: BlockCipher.IV_SIZE],
            ciphertext[BlockCipher.IV_SIZE :],
        )
        key = key.encode("utf-8")
        key = (
            key[: BlockCipher.MAX_KEY_SIZE]
            if len(key) >= BlockCipher.MAX_KEY_SIZE
            else BlockCipher.pad(key)
        )
        cipher = AES.new(key, AES.MODE_CFB, iv)
        d = deferToThread(cipher.decrypt, ciphertext)
        d.addCallback(lambda text: BlockCipher.unpad(text))
        # XXX: cipher.decrypt gives no way to make the distinction between
        # a decrypted empty value and a decryption failure... both return
        # the empty value. Fortunately, we detect empty passwords beforehand
        # thanks to the "leave_empty" parameter which is used by default.
        d.addCallback(lambda text: text.decode("utf-8") if text else None)
        return d

    @classmethod
    def getRandomKey(cls, size=None, base64=False):
        """Return a random key suitable for block cipher encryption.

        Note: a good value for the key length is to make it as long as the block size.

        @param size: key length in bytes, positive or null (default: BlockCipher.IV_SIZE)
        @param base64: if True, encode the result to base-64
        @return: str (eventually base-64 encoded)
        """
        if size is None or size < 0:
            size = BlockCipher.IV_SIZE
        key = urandom(size)
        return b64encode(key) if base64 else key

    @classmethod
    def pad(self, s):
        """Method from http://stackoverflow.com/a/12525165"""
        bs = BlockCipher.BLOCK_SIZE
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    @classmethod
    def unpad(self, s):
        """Method from http://stackoverflow.com/a/12525165"""
        return s[0 : -ord(s[-1])]


class PasswordHasher(object):

    SALT_LEN = 16  # 128 bits

    @classmethod
    def hash(cls, password, salt=None, leave_empty=True):
        """Hash a password.

        @param password (str): the password to hash
        @param salt (base-64 encoded str): if not None, use the given salt instead of a random value
        @param leave_empty (bool): if True, empty password will be returned "as is"
        @return: Deferred: base-64 encoded str
        """
        if leave_empty and password == "":
            return succeed(password)
        salt = (
            b64decode(salt)[: PasswordHasher.SALT_LEN]
            if salt
            else urandom(PasswordHasher.SALT_LEN)
        )
        d = deferToThread(PBKDF2, password, salt)
        d.addCallback(lambda hashed: b64encode(salt + hashed))
        return d

    @classmethod
    def verify(cls, attempt, hashed):
        """Verify a password attempt.

        @param attempt (str): the attempt to check
        @param hashed (str): the hash of the password
        @return: Deferred: boolean
        """
        leave_empty = hashed == ""
        d = PasswordHasher.hash(attempt, hashed, leave_empty)
        d.addCallback(lambda hashed_attempt: hashed_attempt == hashed)
        return d
