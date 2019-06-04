# Copyright 2015 Lukas Lalinsky
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import datetime
import base64
from .common_pb2 import Rep

__all__ = [
    'Date', 'Time', 'Timestamp', 'DateFromTicks', 'TimeFromTicks', 'TimestampFromTicks',
    'Binary', 'STRING', 'BINARY', 'NUMBER', 'DATETIME', 'ROWID', 'BOOLEAN',
]


def Date(year, month, day):
    """Constructs an object holding a date value."""
    return datetime.date(year, month, day)


def Time(hour, minute, second):
    """Constructs an object holding a time value."""
    return datetime.time(hour, minute, second)


def Timestamp(year, month, day, hour, minute, second):
    """Constructs an object holding a datetime/timestamp value."""
    return datetime.datetime(year, month, day, hour, minute, second)


def DateFromTicks(ticks):
    """Constructs an object holding a date value from the given UNIX timestamp."""
    return Date(*time.localtime(ticks)[:3])


def TimeFromTicks(ticks):
    """Constructs an object holding a time value from the given UNIX timestamp."""
    return Time(*time.localtime(ticks)[3:6])


def TimestampFromTicks(ticks):
    """Constructs an object holding a datetime/timestamp value from the given UNIX timestamp."""
    return Timestamp(*time.localtime(ticks)[:6])


def Binary(value):
    """Constructs an object capable of holding a binary (long) string value."""
    if isinstance(value, _BinaryString):
        return value
    return _BinaryString(base64.b64encode(value))


def time_from_java_sql_time(n):
    dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=n)
    return dt.time()


def time_to_java_sql_time(t):
    return ((t.hour * 60 + t.minute) * 60 + t.second) * 1000 + t.microsecond / 1000


def date_from_java_sql_date(n):
    return datetime.date(1970, 1, 1) + datetime.timedelta(days=n)


def date_to_java_sql_date(d):
    if isinstance(d, datetime.datetime):
        d = d.date()
    td = d - datetime.date(1970, 1, 1)
    return td.days


def datetime_from_java_sql_timestamp(n):
    return datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=n)


def datetime_to_java_sql_timestamp(d):
    td = d - datetime.datetime(1970, 1, 1)
    return td.microseconds / 1000 + (td.seconds + td.days * 24 * 3600) * 1000

class _BinaryString(str):
    pass


class ColumnType(object):

    def __init__(self, eq_types):
        self.eq_types = tuple(eq_types)
        self.eq_types_set = set(eq_types)

    def __cmp__(self, other):
        if other in self.eq_types_set:
            return 0
        if other < self.eq_types:
            return 1
        else:
            return -1


STRING = ColumnType(['VARCHAR', 'CHAR'])
"""Type object that can be used to describe string-based columns."""

BINARY = ColumnType(['BINARY', 'VARBINARY'])
"""Type object that can be used to describe (long) binary columns."""

NUMBER = ColumnType(['INTEGER', 'UNSIGNED_INT', 'BIGINT', 'UNSIGNED_LONG', 'TINYINT', 'UNSIGNED_TINYINT', 'SMALLINT', 'UNSIGNED_SMALLINT', 'FLOAT', 'UNSIGNED_FLOAT', 'DOUBLE', 'UNSIGNED_DOUBLE', 'DECIMAL'])
"""Type object that can be used to describe numeric columns."""

DATETIME = ColumnType(['TIME', 'DATE', 'TIMESTAMP', 'UNSIGNED_TIME', 'UNSIGNED_DATE', 'UNSIGNED_TIMESTAMP'])
"""Type object that can be used to describe date/time columns."""

ROWID = ColumnType([])
"""Only implemented for DB API 2.0 compatibility, not used."""

BOOLEAN = ColumnType(['BOOLEAN'])
"""Type object that can be used to describe boolean columns. This is a pyphoenix-specific extension."""

# XXX ARRAY

def typedValueToNative(v):
    if Rep.Name(v.type) == "BOOLEAN" or Rep.Name(v.type) == "PRIMITIVE_BOOLEAN":
        return v.bool_value

    elif Rep.Name(v.type) == "STRING" or Rep.Name(v.type) == "PRIMITIVE_CHAR" or Rep.Name(v.type) == "CHARACTER" or Rep.Name(v.type) == "BIG_DECIMAL":
        return v.string_value

    elif Rep.Name(v.type) == "FLOAT" or Rep.Name(v.type) == "PRIMITIVE_FLOAT" or Rep.Name(v.type) == "DOUBLE" or Rep.Name(v.type) == "PRIMITIVE_DOUBLE":
        return v.double_value

    elif Rep.Name(v.type) == "LONG" or Rep.Name(v.type) == "PRIMITIVE_LONG" or Rep.Name(v.type) == "INTEGER" or Rep.Name(v.type) == "PRIMITIVE_INT" or \
                    Rep.Name(v.type) == "BIG_INTEGER" or Rep.Name(v.type) == "NUMBER" or Rep.Name(v.type) == "BYTE" or Rep.Name(v.type) == "PRIMITIVE_BYTE" or \
                    Rep.Name(v.type) == "SHORT" or Rep.Name(v.type) == "PRIMITIVE_SHORT":
        return v.number_value

    elif Rep.Name(v.type) == "BYTE_STRING":
        return v.bytes_value

    else:
        return None

def javaTypetoNative(java_type):
    if java_type == 'java.math.BigDecimal':
        return ('NUMBER', None, "number_value")
    elif java_type == 'java.lang.Float':
        return ('FLOAT', float, "double_value")
    elif java_type == 'java.lang.Double':
        return ('DOUBLE', None, "double_value")
    elif java_type == 'java.lang.Long':
        return ('LONG', None, "number_value")
    elif java_type == 'java.lang.Integer':
        return ('INTEGER', int, "number_value")
    elif java_type == 'java.lang.Short':
        return ('SHORT', int, "number_value")
    elif java_type == 'java.lang.Byte':
        return ('BYTE', Binary, "bytes_value")
    elif java_type == 'java.lang.Boolean':
        return ('BOOLEAN', bool, "bool_value")
    elif java_type == 'java.lang.String':
        return ('STRING', None, "string_value")
    elif java_type == 'java.sql.Time':
        return ('JAVA_SQL_TIME', time_from_java_sql_time, "number_value")
    elif java_type == 'java.sql.Date':
        return ('JAVA_SQL_DATE', date_from_java_sql_date, "number_value")
    elif java_type == 'java.sql.Timestamp':
        return ('JAVA_SQL_TIMESTAMP', datetime_from_java_sql_timestamp, "number_value")
    elif java_type == '[B':
        return ('BYTE_STRING', Binary, "bytes_value")
        #elif java_type == 'org.apache.phoenix.schema.types.PhoenixArray':
        #    return ('ARRAY', None)
    else:
        return ('NULL', None)
