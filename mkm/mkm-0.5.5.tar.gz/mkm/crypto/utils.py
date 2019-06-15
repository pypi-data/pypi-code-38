# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2019 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

"""
    Utilities
    ~~~~~~~~~

    Crypto utilities
"""

import hashlib
import base58
import base64


def sha256(data: bytes) -> bytes:
    """ SHA-256 """
    # return SHA256.new(data).digest()
    return hashlib.sha256(data).digest()


def ripemd160(data: bytes) -> bytes:
    """ RIPEMD-160 """
    hash_obj = hashlib.new('ripemd160')
    hash_obj.update(data)
    return hash_obj.digest()


def base58_encode(data: bytes) -> str:
    """ BASE-58 Encode """
    return base58.b58encode(data).decode('utf-8')


def base58_decode(string: str) -> bytes:
    """ BASE-58 Decode """
    return base58.b58decode(string)


def base64_encode(data: bytes) -> str:
    """ BASE-64 Encode """
    return base64.b64encode(data).decode('utf-8')


def base64_decode(string: str) -> bytes:
    """ BASE-64 Decode """
    return base64.b64decode(string)
