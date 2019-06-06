#
# Copyright (c) 2019 UCT Prague.
# 
# utils.py is part of Invenio Explicit ACLs 
# (see https://github.com/oarepo/invenio-explicit-acls).
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""Utility functions."""
import json

from invenio_jsonschemas import current_jsonschemas
from invenio_search import current_search
from invenio_search.utils import schema_to_index as invenio_schema_to_index
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, TypeDecorator

from invenio_explicit_acls.proxies import current_explicit_acls


def schema_to_index(schema):
    """Converts schema to a pair of (index, doctype)."""
    index_names = current_search.mappings.keys()
    index, doc_type = invenio_schema_to_index(schema, index_names=index_names)
    if index is None:
        raise AttributeError('No index found for schema %s' % schema)
    return index, doc_type


class ArrayType(TypeDecorator):
    """
    Sqlite-like does not support arrays, so let's use a custom type decorator.

    See http://docs.sqlalchemy.org/en/latest/core/types.html#sqlalchemy.types.TypeDecorator
    """

    impl = String

    def __init__(self, impl_type, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.impl = impl_type

    def process_bind_param(self, value, dialect):
        """Receive a bound parameter value to be converted."""
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        """Receive a result-row column value to be converted."""
        return json.loads(value)

    def copy(self):
        """Produce a copy of this :class:`.TypeDecorator` instance."""
        return ArrayType(self.impl.length)


def convert_relative_schema_to_absolute(x):
    """Convert relative record schema to absolute if needed."""
    if x.startswith('http://') or x.startswith('https://'):
        return x
    return current_jsonschemas.path_to_url(x)


class AllowedSchemaMixin(object):
    """A mixin that keeps allowed and preferred schema. Not to be used directly."""

    # DO NOT forget to set these up in subclasses
    ALLOWED_SCHEMAS = ()
    PREFERRED_SCHEMA = None
    _RESOLVED = False

    @classmethod
    def _prepare_schemas(cls):
        """Converts ALLOWED_SCHEMAS and PREFERRED_SCHEMA to absolute urls."""
        if not cls._RESOLVED:
            cls.ALLOWED_SCHEMAS = tuple(convert_relative_schema_to_absolute(x) for x in cls.ALLOWED_SCHEMAS)
            cls.PREFERRED_SCHEMA = convert_relative_schema_to_absolute(cls.PREFERRED_SCHEMA)
            cls._RESOLVED = True

    @classmethod
    def _convert_and_get_schema(cls, data):
        """Locate $schema in data and if needed convert it to absolute. Returns the converted schema."""
        cls._prepare_schemas()
        schema = data.get('$schema')
        if schema:
            absolute_schema = convert_relative_schema_to_absolute(schema)
            if schema != absolute_schema:
                schema = absolute_schema
                data['$schema'] = absolute_schema
        return schema


def get_record_acl_enabled_schema(record):
    """Returns a normalized schema path for record that is under ACL or None otherwise."""
    schema = record.get('$schema')
    if not schema:
        return  # pragma no cover

    schema = current_jsonschemas.url_to_path(schema) or schema
    if schema not in current_explicit_acls.enabled_schemas:
        return  # pragma no cover

    return schema
