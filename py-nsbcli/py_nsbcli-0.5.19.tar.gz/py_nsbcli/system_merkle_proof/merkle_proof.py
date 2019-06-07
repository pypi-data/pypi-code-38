
"""
"""

import base64
import json


class MerkleProof(object):
    def __init__(self, mtype, proof, key, value):
        self.mtype = mtype
        self.proof = proof
        self.key = key
        self.value = value

    @property
    def mtype(self):
        return self._mtype

    @mtype.setter
    def mtype(self, val: int):
        if not isinstance(val, int):
            raise TypeError("mtype require integer")
        self._mtype = val

    @property
    def proof(self):
        return self._proof

    @proof.setter
    def proof(self, val: bytes):
        if not isinstance(val, bytes):
            raise TypeError("proof require bytes")
        self._proof = val

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, val: bytes):
        if not isinstance(val, bytes):
            raise TypeError("key require bytes")
        self._key = val

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val: bytes):
        if not isinstance(val, bytes):
            raise TypeError("value require bytes")
        self._value = val

    def dict(self):
        return {
            '1': self._mtype,
            '2': base64.b64encode(self._proof).decode() if self._proof is not None else None,
            '3': base64.b64encode(self._key).decode() if self._key is not None else None,
            '4': base64.b64encode(self._value).decode() if self._value is not None else None,
        }

    def json(self):
        return json.dumps(self.dict())


if __name__ == '__main__':
    pass
