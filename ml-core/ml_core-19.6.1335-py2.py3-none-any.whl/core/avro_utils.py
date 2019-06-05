# -*- coding: utf-8 -*-
import six
import json

from missinglink.core.json_utils import clean_system_keys_iter, get_json_items


class AvroWriterErrors(Exception):
    pass


class AvroWriter(object):
    def __init__(self, write_to=None, key_name=None, schema=None):
        self.__key_name = key_name
        self.__write_to = write_to or six.BytesIO()
        self.__writer = None
        self.__schema_so_far = schema or {}
        self.__items_so_far = []

    @property
    def stream(self):
        return self.__write_to

    @classmethod
    def _get_schema_type(cls, val):
        type_convert = {'str': 'string', 'bool': 'boolean', 'unicode': 'string', 'int': 'long'}

        t = type(val).__name__
        t = type_convert.get(t, t)
        return t

    @classmethod
    def get_schema_from_item(cls, schema_so_far, item):
        has_nulls = False
        for key, val in item.items():
            if key in schema_so_far:
                continue

            if val is None:
                has_nulls = True
                continue

            schema_so_far[key] = cls._get_schema_type(val)

        return has_nulls

    @classmethod
    def __create_schema_for_fields(cls, schema_fields):
        import avro

        schema_data = {
            "namespace": "ml.data",
            "type": "record",
            "name": "Data",
            "fields": [],
        }

        for key, t in schema_fields.items():
            field_data = {'name': key, 'type': [t, 'null']}
            schema_data['fields'].append(field_data)

        parse_method = getattr(avro.schema, 'parse', None) or getattr(avro.schema, 'Parse')
        data = json.dumps(schema_data)
        return parse_method(data)

    def close(self):
        self.__write_items_so_far()

        if self.__writer is None:
            return

        self.__writer.flush()

    @classmethod
    def __validate_item(cls, expected_schema, datum):
        from avro.io import INT_MIN_VALUE, INT_MAX_VALUE, LONG_MIN_VALUE, LONG_MAX_VALUE

        """Determine if a python datum is an instance of a schema."""
        schema_type = expected_schema.type
        if schema_type == 'null':
            return datum is None
        elif schema_type == 'boolean':
            return isinstance(datum, bool)
        elif schema_type == 'string':
            return isinstance(datum, six.string_types)
        elif schema_type == 'bytes':
            return isinstance(datum, six.binary_type)
        elif schema_type == 'int':
            return isinstance(datum, six.integer_types) and INT_MIN_VALUE <= datum <= INT_MAX_VALUE
        elif schema_type == 'long':
            return isinstance(datum, six.integer_types) and LONG_MIN_VALUE <= datum <= LONG_MAX_VALUE
        elif schema_type in ['float', 'double']:
            return isinstance(datum, six.integer_types + (float, ))
        elif schema_type == 'fixed':
            return isinstance(datum, six.binary_type) and len(datum) == expected_schema.size
        elif schema_type == 'enum':
            return datum in expected_schema.symbols
        elif schema_type in ['union', 'error_union']:
            return True in [cls.__validate_item(s, datum) for s in expected_schema.schemas]

    @classmethod
    def __validate(cls, expected_schema, datum):
        schema_type = expected_schema.type

        if schema_type not in ['record']:
            raise Exception('unknown schema type "{}"'.format(schema_type))

        for f in expected_schema.fields:
            if not cls.__validate_item(f.type, datum.get(f.name)):
                val = datum.get(f.name)
                yield (f.name, f.type.schemas[0].type, cls._get_schema_type(val), val)

    def __write_multi(self, items):
        from avro.io import AvroTypeException

        errors = []

        for i, item in enumerate(items):
            try:
                self.__writer.append(item)
            except AvroTypeException:
                avro_schema = self.__create_schema_for_fields(self.__schema_so_far)
                for name, expected_type, actual_type, value in self.__validate(avro_schema, item):
                    errors.append('{name}: excepted type {expected_type} got {actual_type} ({value})'.format(
                        i=i, name=name, expected_type=expected_type, actual_type=actual_type, value=value))

        if len(errors) > 0:
            raise AvroWriterErrors('\n'.join(errors))

    def __create_writer_if_needed(self, schema):
        if self.__writer is not None:
            return

        from avro.datafile import DataFileWriter
        from avro.io import DatumWriter

        avro_schema = self.__create_schema_for_fields(schema)
        self.__writer = DataFileWriter(self.__write_to, DatumWriter(), avro_schema)

    def __write_items_so_far(self):
        self.__create_writer_if_needed(self.__schema_so_far)
        self.__write_multi(self.__items_so_far)

        self.__items_so_far = []

    def __write_first_items(self, data_iter):
        if self.__writer is not None:
            return []

        has_nulls = True

        for item in data_iter:
            has_nulls = self.get_schema_from_item(self.__schema_so_far, item)

            self.__items_so_far.append(item)

            if has_nulls:
                continue

            break

        if has_nulls:
            return []

        self.__write_items_so_far()

    def __write_the_rest(self, data_iter):
        for item in data_iter:
            self.__writer.append(item)

    def append_data(self, data):
        data_iter = clean_system_keys_iter(get_json_items(data, key_name=self.__key_name))

        self.__write_first_items(data_iter)
        self.__write_the_rest(data_iter)
