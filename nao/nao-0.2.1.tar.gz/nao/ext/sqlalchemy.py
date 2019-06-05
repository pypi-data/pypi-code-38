
from sqlalchemy.types import TypeDecorator, String, Integer, UnicodeText

from .yaml import load, dump


# TODO move custom types to nao
class MAC(TypeDecorator):
    """Represents a MAC address in 6 bytes.

    """
    impl = String(6)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        return ''.join([chr(int(i, 16)) for i in value.split(':')])

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        
        return ':'.join(['{:0>2x}'.format(ord(i)).upper() for i in value])


class HexID(TypeDecorator):
    """Represents an 8 digit hexadecimal ID

    """
    impl = Integer

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        return int(value, 16)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        
        return '{:0>8x}'.format(value).upper()


class YAML(TypeDecorator):
    """Represents an 8 digit hexadecimal ID

    """
    impl = UnicodeText

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        return dump(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        
        return load(value)