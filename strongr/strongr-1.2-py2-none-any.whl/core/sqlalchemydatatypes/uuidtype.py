from sqlalchemy.types import TypeDecorator, CHAR

from sqlalchemy.dialects.postgresql import UUID as POSTGRESQL_UUID
from sqlalchemy.dialects.mysql import BINARY as MYSQL_BINARY
import uuid


# source: http://docs.sqlalchemy.org/en/latest/core/custom_types.html

class UUIDType(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type or mysql's binary type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(POSTGRESQL_UUID())
        elif dialect.name == 'mysql':
            return dialect.type_descriptor(MYSQL_BINARY(16))
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        elif dialect.name == 'mysql':
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value).bytes
            else:
                return value.bytes
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'mysql':
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(bytes=value)
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value
