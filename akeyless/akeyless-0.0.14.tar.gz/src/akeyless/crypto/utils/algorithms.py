from enum import Enum


class CryptoAlgorithm(Enum):

    __rlookup__ = {}  # name -> CryptoAlgorithm

    AES_128_GCM = ("AES128GCM", 16, False)
    AES_256_GCM = ("AES256GCM", 32, False)

    RSA_1024 = ("RSA1024", 1024, False)
    RSA_2048 = ("RSA2048", 2048, False)

    def __init__(self, alg_name, key_len, deterministic):
        # type: (str, int, bool) -> None
        self._alg_name = alg_name
        self._key_len = key_len
        self._deterministic = deterministic
        self.__rlookup__[alg_name] = self

    @classmethod
    def get_alg_by_name(cls, alg_name):
        # type: (str) -> CryptoAlgorithm
        return cls.__rlookup__[alg_name]

    @property
    def alg_name(self):
        # type: () -> str
        return self._alg_name

    @property
    def key_len(self):
        # type: () -> int
        return self._key_len

    def is_deterministic(self):
        # type: () -> bool
        return self._deterministic

    def is_aes(self):
        # type: () -> bool
        return self._alg_name in ("AES128GCM", "AES256GCM")

    def is_rsa(self):
        # type: () -> bool
        return self._alg_name in ("RSA1024", "RSA2048")
