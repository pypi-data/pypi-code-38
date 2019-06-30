from typing import *
from struct import pack
import time
import base58
import hashlib


class HashCipher(object):
    def __init__(self, salt=None, cipher=hashlib.blake2b):
        self._salt: Optional[bytes] = salt or b''
        self._cipher = cipher

    def hash(self, text) -> str:
        cipher = self._cipher(salt=self._salt)
        cipher.update(text.encode("utf8"))
        return cipher.hexdigest()

    def digest(self, text) -> bytes:
        cipher = self._cipher(salt=self._salt)
        cipher.update(text.encode("utf8"))
        return cipher.digest()


def create_base58_key(
        data,
        length: int = 16,
        prefix: str = "",
        salt: Optional[str]= None,
        cipher=hashlib.blake2b,
        timestamp: bool = False,
) -> str:
    hash_cipher = HashCipher(salt=salt, cipher=cipher)
    hash_key = hash_cipher.digest(str(data))
    slice_key = base58.b58encode(hash_key)
    if type(slice_key) is bytes:
        slice_key = slice_key.decode("utf8")
    time_part = ''
    if timestamp:
        now_timestamp = int(time.time() * 1000)
        time_part = base58.b58encode(pack('>Q', now_timestamp)).zfill(10).decode("utf8")
    key = f'{prefix}{"{}{}".format(time_part, slice_key)[:length]}'
    return key


__all__ = ["create_base58_key", ]
