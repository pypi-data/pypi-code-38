from peewee import *


class SASField(BigIntegerField):
    """
    Custom Field that Holds SAS addresses.
    """

    def db_value(self, value) -> int:
        """
        Translate from str into int
        :param value: string with SAS address
        :return: int with MAC value
        """
        if value is not None:
            if type(value) != int:
                return int(value.replace(':', '').replace('.', '').replace('-', ''), 16)
            else:
                return value

    def python_value(self, value: int):
        """
        Translate from int into str
        :param value: int with MAC value
        :return: string with MAC address
        """
        if value is not None:
            mac_hex = "{:012x}".format(value)
            sas_str = ":".join(mac_hex[i:i + 2] for i in range(0, len(mac_hex), 2))
            return sas_str


class MACField(BigIntegerField):
    """
    Custom Field that holds MAC addresses.
    """

    def db_value(self, value) -> int:
        """
        Translate from str into int
        :param value: string with MAC address
        :return: int with MAC value
        """
        if value is not None:
            if type(value) != int:
                return int(value.replace(':', '').replace('.', '').replace('-', ''), 16)
            else:
                return value

    def python_value(self, value) -> str:
        """
        Translate from int into str
        :param value: int with MAC value
        :return: string with MAC address
        """
        if value is not None:
            mac_hex = "{:012x}".format(value)
            mac_str = ":".join(mac_hex[i:i + 2] for i in range(0, len(mac_hex), 2))
            return mac_str


class IntegerBase36Field(BigIntegerField):
    """
    Custom Field that holds Integers in base36 representation.
    """

    def db_value(self, value):
        """
        Translate from str that int36 into int or in case of just int simply pass it.
        :param value: string with int36 value or int value
        :return: int
        """
        if value is not None:
            if type(value) is str:
                return int(value, 36)
            elif type(value) is int:
                return value

    def python_value(self, value):
        """
        Translate from int into str that int36
        :param value: int value
        :return: string with int36 value
        """
        if value is not None:
            alphabet, base36 = ['0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', '']

            while value:
                value, i = divmod(value, 36)
                base36 = alphabet[i] + base36

            return base36 or alphabet[0]
