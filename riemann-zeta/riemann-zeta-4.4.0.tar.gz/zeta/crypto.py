import os
import hashlib

from riemann.utils import sha256, hash256  # noqa: F401

import ecdsa
from ecdsa.ecdsa import int_to_string

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

from typing import Union


DB_PBKDF_SALT = b'summa-zeta-key-stretching'
PBKDF_ITERATIONS = 100000


def pbkdf2_hmac(data: bytes,
                salt: bytes = b'',
                hash_name: str = 'sha512',
                iterations: int = 2048) -> bytes:  # pragma: nocover
    ''' Key stretching function PBKDF2 using HMAC-SHA512
    Args:
        data       (bytes): data to stretch, mnemonic for BIP39
        salt       (bytes): optional data for security, 'mnemonic' for BIP39
        hash_name  (str): HMAC hash digest algorithm, SHA512 for BIP39
        iterations (int): number of HMAC-SHA512 hashing rounds, 2048 for BIP39
    Returns:
        (bytes): generated seed, 512-bit seed for BIP39
    '''
    return hashlib.pbkdf2_hmac(hash_name, data, salt, iterations)


def _aes_encrypt_with_iv(
        key: bytes,
        iv: bytes,
        data_bytes: bytes) -> bytes:  # pragma: no cover
    '''Encrypts a message with a key.
    Args:
        key         (bytes): the AES key (32 bytes)
        iv          (bytes): the AES initialization vector
        data_bytes  (bytes): the message to encrypt
    Returns:
        (bytes): the encrypted message
    '''
    data_bytes = pad(data_bytes, 16)
    e = AES.new(key, AES.MODE_CBC, iv).encrypt(data_bytes)
    return e


def _aes_decrypt_with_iv(
        key: bytes,
        iv: bytes,
        data_bytes: bytes) -> bytes:  # pragma: no cover
    '''Decrypts a message with a key.
    Args:
        key         (bytes): the AES key (32 bytes)
        iv          (bytes): the AES initialization vector
        data_bytes  (bytes): the message to decrypt
    Returns:
        (bytes): the decrypted message
    '''
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data_bytes = cipher.decrypt(data_bytes)
    try:
        return unpad(data_bytes, 16)
    except ValueError as e:
        e.args += ('Invalid passphrase',)
        raise e


def encode_aes(
        message_bytes: bytes,
        secret_phrase: str) -> bytes:  # pragma: no cover
    '''Encrypts a message with a phrase
    Args:
        message_bytes   (bytes): the bytes to encrypt
        secret_phrase     (str): the user's db encryption phrase
    Returns:
        (bytes): the encrypted message, prepended with its iv and ephemeral key
    '''
    secret = pbkdf2_hmac(
        data=secret_phrase.encode('utf-8'),
        salt=DB_PBKDF_SALT,
        hash_name='sha256',
        iterations=PBKDF_ITERATIONS)

    # NB: New iv and ephemeral key are created each time we encrypt
    iv = os.urandom(16)
    tmp_key = os.urandom(32)
    enc_tmp_key = _aes_encrypt_with_iv(secret, iv, tmp_key)

    ciphertext = _aes_encrypt_with_iv(tmp_key, iv, message_bytes)

    # NB: we prepend the ciphertext with its iv (16 bytes)
    #     and the ephemeral key (48 bytes)
    encrypted_message_bytes = iv + enc_tmp_key + ciphertext
    return encrypted_message_bytes


def decode_aes(
        encrypted_message: bytes,
        secret_phrase: str) -> bytes:  # pragma: no cover
    '''Decrypts a message with a phrase
    Args:
        encrypted_message (bytes): the encrypted message, prepended with
                                         its iv and ephemeral key
        secret_phrase             (str): the user's db encryption phrase
    Returns:
        (bytes): the decrypted message
    '''
    secret = pbkdf2_hmac(
        data=secret_phrase.encode('utf-8'),
        salt=DB_PBKDF_SALT,
        hash_name='sha256',
        iterations=PBKDF_ITERATIONS)

    # NB: Extract the iv and encrypted key from the message
    iv = encrypted_message[:16]
    enc_tmp_key = encrypted_message[16:64]
    encrypted_message = encrypted_message[64:]

    # NB: Decrypt the key and use it to decrypt the message
    tmp_key = _aes_decrypt_with_iv(secret, iv, enc_tmp_key)
    message_bytes = _aes_decrypt_with_iv(tmp_key, iv, encrypted_message)

    return message_bytes


def is_pubkey(p: str) -> bool:
    '''
    determines if a string can be interpreted as btc hex formatted pubkey
    '''
    prefix = p[0:2]
    try:
        bytes.fromhex(p)
    except ValueError:
        return False
    if len(p) == 66:   # compressed
        return prefix in ['02', '03']
    if len(p) == 130:  # uncompressed
        return prefix == '04'
    return False


def coerce_key(data: Union[str, bytes]) -> ecdsa.SigningKey:
    ''' Coerces key data to an ECDSA SigningKey object

    Args:
        data (*): A key in some supported format
    Returns:
        (ecdsa.SigningKey): The key object
    '''
    if isinstance(data, str):
        data = bytes.fromhex(data)

    return ecdsa.SigningKey.from_string(
        data,
        curve=ecdsa.SECP256k1)


# ---------------------------------------------------------
#
# Copyright 2014 Corgan Labs
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


def to_pubkey(privkey_obj: ecdsa.SigningKey) -> bytes:  # pragma: nocover
    """
    Return compressed public key encoding
    Adapted from prusnak's bip32utils
    https://github.com/prusnak/bip32utils/
    https://github.com/prusnak/bip32utils/blob/master/LICENSE
    """
    pubkey_obj = privkey_obj.get_verifying_key()
    padx = (b'\0' * 32 + int_to_string(pubkey_obj.pubkey.point.x()))[-32:]
    if pubkey_obj.pubkey.point.y() & 1:
        ck = b'\3' + padx
    else:
        ck = b'\2' + padx
    return ck


def pow_mod(x: int, y: int, z: int) -> int:  # pragma: nocover
    '''
    int, int, int (or float)
    returns (x^y)mod z
    '''
    number = 1
    while y:
        if y & 1:
            number = number * x % z
        y >>= 1
        x = x * x % z
    return number


def uncompress_pubkey(pubkey: bytes) -> bytes:  # pragma: nocover
    '''
    takes a compressed pubkey, returns the uncompressed pubkey
    '''
    p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
    parity = pubkey[0] - 2
    x = int.from_bytes(pubkey[1:], 'big')
    a = (pow_mod(x, 3, p) + 7) % p
    y = pow_mod(a, (p + 1) // 4, p)
    if y % 2 != parity:
        y = -y % p
    return (x.to_bytes(32, 'big')) + (y.to_bytes(32, 'big'))


def coerce_pubkey(data: Union[str, bytes]) -> ecdsa.VerifyingKey:
    '''Coerces key data to an ECDSA VerifyingKey object

    Args:
        data (*): A pubkey in some supported format
    Returns:
        (ecdsa.VerifyingKey): The key object
    '''
    if isinstance(data, str):
        data = bytes.fromhex(data)

    if len(data) == 33:
        data = uncompress_pubkey(data)
    if len(data) == 65:
        data = data[1:]  # for if there's an 04 in front
    if len(data) != 64:
        raise ValueError('Unsupported pubkey format')
    return ecdsa.VerifyingKey.from_string(
        data,
        curve=ecdsa.SECP256k1)
