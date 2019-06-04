from enum import Enum


class ItemType(Enum):
    __rlookup__ = {}  # name -> ItemType

    AES_128_GCM = ("AES128GCM", True)
    AES_256_GCM = ("AES256GCM", True)

    AES_128_SIV = ("AES128SIV", True)
    AES_256_SIV = ("AES256SIV", True)

    RSA_1024 = ("RSA1024", True)
    RSA_2048 = ("RSA2048", True)

    USER_SECRET = ("USER_SECRET", False)

    def __init__(self, name, is_key):
        # type: (str, bool) -> None
        self._name = name
        self._is_key = is_key
        self.__rlookup__[name] = self

    @classmethod
    def get_by_name(cls, name):
        # type: (str) -> ItemType
        return cls.__rlookup__[name]

    @property
    def name(self):
        # type: () -> str
        return self._name

    @property
    def is_key(self):
        # type: () -> bool
        return self._is_key

    @classmethod
    def key_types(cls):
        # type: () -> list
        return list(map(lambda t: t.name, filter(lambda t: t.is_key, cls.__rlookup__.values())))

    @classmethod
    def secret_types(cls):
        # type: () -> list
        return list(map(lambda t: t.name, filter(lambda t: not t.is_key, cls.__rlookup__.values())))
