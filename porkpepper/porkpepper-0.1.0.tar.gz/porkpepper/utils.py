from typing import *
from struct import pack
import time
import base58
import hashlib


class HashCipher(object):
    def __init__(self, salt=None, cipher=hashlib.sha3_256):
        self._salt = salt
        self._cipher = cipher

    def hash(self, text) -> str:
        binary = (self._salt + text).encode("utf8") if self._salt else text.encode("utf8")
        return self._cipher(binary).hexdigest()

    def digest(self, text) -> bytes:
        binary = (self._salt + text).encode("utf8") if self._salt else text.encode("utf8")
        return self._cipher(binary).digest()


def create_base58_key(
        data,
        length: int = 16,
        prefix: str = "",
        salt: Optional[str]= None,
        cipher=hashlib.sha3_256,
        timestamp: bool = False,
) -> str:
    hash_cipher = HashCipher(salt=salt, cipher=cipher)
    hash_key = hash_cipher.digest(str(data))
    slice_key = base58.b58encode(hash_key)[:length]
    if type(slice_key) is bytes:
        slice_key = slice_key.decode("utf8")
    time_part = ''
    if timestamp:
        time_part = base58.b58encode(pack('>Q', int(time.time() * 1000))).zfill(10).decode("utf8")
    key = "{}{}{}".format(prefix, time_part, slice_key)
    return key


__all__ = ["create_base58_key", ]
