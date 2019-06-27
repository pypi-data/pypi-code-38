"""
Marshmallow tool kit will be used by backend api projects
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from bson import UUIDLegacy, Binary
from marshmallow import Schema, pre_dump, post_load, post_dump, pre_load, fields
from marshmallow.fields import DateTime, UUID

from .constants import (MARSHMALLOW_NESTED_FIELDS, MARSHMALLOW_LIST_FIELDS, MARSHMALLOW_DICT_FIELDS,
                        MARSHMALLOW_SCALAR_FIELDS, MONGO_ID_FIELD_NAME, POTENTIAL_MONGO_ID_FIELD_NAME)
from .utils_kit import build_mongodb_uuid, convert_py_uuid_to_mongodb_uuid


############################################################
# Customized marshmallow fields
############################################################

class MongoUUID(fields.UUID):
    """
    Convert value between uuid string to Mongo UUID(bson.binary.Binary)
    """

    def _serialize(self, value, attr, obj):
        """
        Convert MONGO UUID (Binary) to string
        """
        value = uuid.UUID(bytes=value) if value and isinstance(value, Binary) else value
        return super()._serialize(value, attr, obj)

    def _deserialize(self, value, attr, data):
        """
        Convert str to Mongo UUID
        """
        value = super()._deserialize(value, attr, data)
        if not value:
            return value
        return convert_py_uuid_to_mongodb_uuid(value)


class IntegerTimeStamp(DateTime):
    """
    Convert value between int and datetime string
    """

    def _serialize(self, value, attr, obj):
        """
        Convert a **integer** timestamp value & **string** datetime  value
        """
        if isinstance(value, int):
            value = datetime.utcfromtimestamp(value)
        return super()._serialize(value, attr, obj)

    def _deserialize(self, value, attr, data):
        """
        Convert a **string** datetime  value to **integer** timestamp  value
        """
        value = super()._deserialize(value, attr, data)
        if not value:
            return None
        return int(value.timestamp())


class DecimalTimeStamp(DateTime):
    """
    Convert value between **Decimal** timestamp value and **string** datetime  value
    """

    def _serialize(self, value, attr, obj):
        """
        Convert a **Decial** timestamp value to **string** datetime  value
        """
        if isinstance(value, Decimal):
            value = datetime.utcfromtimestamp(float(value))
        return super()._serialize(value, attr, obj)

    def _deserialize(self, value, attr, data):
        """
        Convert a **string** datetime  value to **Decimal** timestamp value
        """
        value = super()._deserialize(value, attr, data)
        if not value:
            return None
        return Decimal(value.timestamp())


############################################################
# Customized Base Schema which will by used by all other api projects
############################################################
class SchemaMongoMixin:
    """
    This mixin class will help marshmallow schema class generate a collection of valid mongo-style query field names
    """

    @pre_dump
    def pre_dump_process(self, data):
        data['id'] = data.get(MONGO_ID_FIELD_NAME, None)
        data = self._extra_pre_dump_process(data)
        return data

    def _extra_pre_dump_process(self, data):
        """
        Any other extra pre dump process can be added here
        """
        return data

    @post_dump
    def post_dump_process(self, data):
        data = self._extra_post_dump_process(data)
        return data

    def _extra_post_dump_process(self, data):
        """
        Any other extra post dump process can be added here
        """
        return data

    @pre_load
    def pre_load_process(self, data):

        data = {key: value for key, value in data.items()}

        # NOTE: 
        #   1. in create case, normally don't have 'id'/'_id' field
        #   2. in update case, if the 'id' field exists in payload, keep it instead of create new one 
        #   3. in rare case the '_id' field exists in payload, then pass it to 'id'

        if not data.get(POTENTIAL_MONGO_ID_FIELD_NAME, None) and not data.get(MONGO_ID_FIELD_NAME, None):
            data[POTENTIAL_MONGO_ID_FIELD_NAME] = uuid.uuid4().hex
        elif data.get(MONGO_ID_FIELD_NAME, None):
            data[POTENTIAL_MONGO_ID_FIELD_NAME] = data.pop(MONGO_ID_FIELD_NAME)

        data = self._extra_pre_load_process(data)
        return data

    def _extra_pre_load_process(self, data):
        """
        Any other extra pre load process can be added here
        """
        return data

    @post_load
    def post_load_process(self, data):

        # auto generate these field after load data from client input
        if 'created_at' not in data:
            data['created_at'] = datetime.now().astimezone(timezone.utc)

        if 'updated_at' not in data:
            data['updated_at'] = datetime.now().astimezone(timezone.utc)

        # always make sure mongo default id name '_id' in the loaded data 
        if data.get(POTENTIAL_MONGO_ID_FIELD_NAME, None):
            data[MONGO_ID_FIELD_NAME] = data.pop(POTENTIAL_MONGO_ID_FIELD_NAME)

        data = self._extra_post_load_process(data)
        return data

    def _extra_post_load_process(self, data):
        """
        Any other extra post load process can be added here
        """
        return data

    @classmethod
    def valid_mongo_query_fields(cls) -> dict:
        """
        Use class level cache Schema's valid mongo style's query  field names to avoid call the real method repeatedly
        :return: a set of valid query field name and its marshmallow type
        """
        if getattr(cls, '_valid_mongo_query_fields', False):
            return getattr(cls, '_valid_mongo_query_fields')

        def _fetch_valid_field_name_from_schema_fields(prefix: str = '', fields: dict = None):

            field_names = {}

            for field, value in fields.items():

                sub_prefix = '{}.{}'.format(prefix, field) if prefix else field

                # Nested field
                if isinstance(value, MARSHMALLOW_NESTED_FIELDS):
                    field_names.update(
                        _fetch_valid_field_name_from_schema_fields(sub_prefix, value.nested._declared_fields),
                    )
                    continue

                # List fields
                if isinstance(value, MARSHMALLOW_LIST_FIELDS):
                    if isinstance(value.container, MARSHMALLOW_NESTED_FIELDS):
                        try:
                            field_names.update(
                                _fetch_valid_field_name_from_schema_fields(sub_prefix, value.container.nested.fields))
                        except AttributeError:
                            continue
                        else:
                            continue

                # Dict fields
                if isinstance(value, MARSHMALLOW_DICT_FIELDS):
                    field_names.update(_fetch_valid_field_name_from_schema_fields(sub_prefix, value.metadata))
                    continue

                # Scalar value field
                if isinstance(value, MARSHMALLOW_SCALAR_FIELDS):
                    field_dump_to = value.dump_to
                    if not field_dump_to:
                        field_names.update({sub_prefix: type(value)})
                    else:
                        field_names.update(
                            {'.'.join(sub_prefix.split('.')[0:-1] + [field_dump_to]) + '->' + field: type(
                                value)})
                        field_names.update(
                            {'.'.join(sub_prefix.split('.')[0:-1] + [field_dump_to]): type(value)})

            return field_names

        valid_mongo_query_fields = _fetch_valid_field_name_from_schema_fields(fields=cls._declared_fields)

        # added mongo's default id field name '_id' to valid field set
        valid_mongo_query_fields.update({MONGO_ID_FIELD_NAME: UUID})
        setattr(cls, '_valid_mongo_query_fields', valid_mongo_query_fields)
        return getattr(cls, '_valid_mongo_query_fields')


class BaseSchema(Schema, SchemaMongoMixin):
    id = MongoUUID(required=False, allow_none=True, description='ID of a schema record')
    created_at = DateTime(required=False, description='Schema creation time')
    updated_at = DateTime(required=False, description='Schema object update time')
    deleted_at = DateTime(required=False, description='Schema object delete time', allow_none=True)
