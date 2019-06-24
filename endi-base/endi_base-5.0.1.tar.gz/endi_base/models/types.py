# -*- coding: utf-8 -*-
"""
    Custom types and usefull functions
"""
import time
import datetime
import simplejson as json

from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import (
    TypeDecorator,
    Integer as Integer_type,
    String as String_type,
    Text as Text_type,
    )

from endi_base.models.utils import (
    format_to_taskdate,
    format_from_taskdate,
)
from .mixins import PersistentACLMixin  # For retrocompatibility


class CustomDateType(TypeDecorator):
    """
        Custom date type used because our database is using
        integers to store date's timestamp
    """
    impl = Integer_type

    def process_bind_param(self, value, dialect):
        if value is None or not value:
            return int(time.time())
        elif isinstance(value, datetime.datetime):
            return int(time.mktime(value.timetuple()))
        elif isinstance(value, int):
            return value
        return time.mktime(value.timetuple())

    def process_result_value(self, value, dialect):
        if value:
            return datetime.datetime.fromtimestamp(float(value))
        else:
            return datetime.datetime.now()


class CustomDateType2(TypeDecorator):
    """
        Custom date type used because our database is using
        custom integers to store dates
        YYYYMMDD
    """
    impl = Integer_type

    def process_bind_param(self, value, dialect):
        return format_to_taskdate(value)

    def process_result_value(self, value, dialect):
        return format_from_taskdate(value)


class CustomFileType(TypeDecorator):
    """
    Custom Filetype used to glue deform fileupload tools with
    the database element
    """
    impl = String_type

    def __init__(self, prefix, *args, **kw):
        TypeDecorator.__init__(self, *args, **kw)
        self.prefix = prefix

    def process_bind_param(self, value, dialect):
        """
            process the insertion of the value
            write the file to persistent storage
        """
        ret_val = None
        if isinstance(value, dict):
            ret_val = value.get('filename', '')
        return ret_val

    def process_result_value(self, value, dialect):
        """
            Get the datas from database
        """
        if value:
            return dict(filename=value,
                        uid=self.prefix + value)
        else:
            return dict(filename="",
                        uid=self.prefix)


class CustomInteger(TypeDecorator):
    """
        Custom integer, allow long to int automatic conversion
    """
    impl = Integer_type

    def process_bind_param(self, value, dialect):
        """
            On insertion
        """
        if isinstance(value, long):
            value = int(value)
        return value

    def process_result_value(self, value, dialect):
        """
            On query
        """
        if isinstance(value, long):
            value = int(value)
        return value


class JsonEncodedDict(TypeDecorator):
    """
    Stores a dict as a json string in the database
    """
    impl = Text_type

    def process_bind_param(self, value, dialect):
        """
            Process params when setting the value
        """
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        """
            Processing the value when getting the value
        """
        if value is not None:
            value = json.loads(value)
        return value


class JsonEncodedList(TypeDecorator):
    """
    Stores a list as a json string
    """
    impl = Text_type

    def process_bind_param(self, value, dialect):
        """
            Process params when setting the value
        """
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        """
            Processing the value when getting the value
        """
        if value is not None:
            value = json.loads(value)
        return value

from pyramid.security import (
    Allow,
    Everyone,
    Authenticated,
    ALL_PERMISSIONS,
)


class ACLType(JsonEncodedList):
    all_permissions_serialized = '__ALL_PERMISSIONS__'
    defaults = [
        (Allow, 'group:admin', ALL_PERMISSIONS),
        (Allow, "group:manager", ("manage", "add", "edit", "view")),
    ]

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = [list(ace) for ace in value if ace not in self.defaults]
            for ace in value:
                if ace[2] == ALL_PERMISSIONS:
                    ace[2] = self.all_permissions_serialized
        return JsonEncodedList.process_bind_param(self, value, dialect)

    def process_result_value(self, value, dialect):
        acl = JsonEncodedList.process_result_value(self, value, dialect)
        if acl is not None:
            for ace in acl:
                if ace[2] == self.all_permissions_serialized:
                    ace[2] = ALL_PERMISSIONS
            return self.defaults + [tuple(ace) for ace in acl]


class MutableDict(Mutable, dict):
    """
        Allows sqlalchemy to check if a data has changed in our dict
        If not used, the dbsession will never detect modifications

        Note : only associating a value to one key will work (no subdict
            handling)
    """
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutableDict."

        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        "Detect dictionary set events and emit change events."

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        "Detect dictionary del events and emit change events."

        dict.__delitem__(self, key)
        self.changed()


class MutableList(Mutable, list):
    """
        Allows sqlalchemy to check if a data has changed in our list
        If not used, the dbsession will never detect modifications
    """
    @classmethod
    def coerce(cls, key, value):
        """
        Convert list to mutablelist
        """
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def append(self, value):
        """
        Detect list append changes
        """
        list.append(self, value)
        self.changed()

    def extend(self, value):
        """
        Detect list append changes
        """
        list.extend(self, value)
        self.changed()

    def remove(self, value):
        """
        Detect list remove change
        """
        list.remove(self, value)
        self.changed()


# Here we always associate our MutableDict to our JsonEncodedDict column type
# If a column is of type JsonEncodedDict, its value will be casted as a
# mutabledict that will signify modifications on setitem and delitem
MutableDict.associate_with(JsonEncodedDict)
# The same for lists
MutableList.associate_with(JsonEncodedList)
