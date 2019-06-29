"""This script contains all the classes related to the module"""

from shadow_auth._internal.enums import Algorithm
from shadow_auth._internal.exceptions import (
    # Exceptions
    InvalidArgumentType,
    InvalidArgumentFormat,

    # Exception Messages
    MESSAGE_GENERIC_INVALID_TYPE,
    MESSAGE_INVALID_HASH_FORMAT,
    MESSAGE_INVALID_SHADOW_FILE_HASH_TYPE
)


class ShadowHash:
    """
    Provide and easy access to the different components of the hashed stored in the shadow file.
    """
    algorithm: str = None
    salt: str = None
    hash: str = None

    def __init__(self, shadow_file_hash: str):
        """
        Init the object attributes based on the shadow_file_hash

        :raises InvalidArgumentType, InvalidArgumentFormat:
        """
        if not isinstance(shadow_file_hash, str):
            raise InvalidArgumentType(MESSAGE_INVALID_SHADOW_FILE_HASH_TYPE)

        _hash_list = shadow_file_hash.split("$")

        if len(_hash_list) != 4:
            raise InvalidArgumentFormat(MESSAGE_INVALID_HASH_FORMAT)

        self.algorithm = _hash_list[1]
        self.salt = _hash_list[2]
        self.hash = _hash_list[3]

    def _get_full_hash(self):
        """Returns the full hash based on the attributes of the object"""
        return "${algorithm}${salt}${hash}".format(algorithm=self.algorithm, salt=self.salt, hash=self.hash)

    def equals(self, hash_to_compare: str) -> bool:
        """
        Compares the attributes of the object against a given string hash

        :param hash_to_compare: String to compare against the attributes of the object
        :return: bool
        :raises InvalidArgumentType:
        """
        if not isinstance(hash_to_compare, str):
            raise InvalidArgumentType(MESSAGE_GENERIC_INVALID_TYPE)

        return self._get_full_hash() == hash_to_compare

