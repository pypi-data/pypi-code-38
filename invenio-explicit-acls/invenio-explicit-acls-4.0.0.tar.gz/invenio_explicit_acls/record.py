#
# Copyright (c) 2019 UCT Prague.
# 
# record.py is part of Invenio Explicit ACLs 
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
"""ACL related mixins for Record class."""
from invenio_jsonschemas import current_jsonschemas
from invenio_records import Record

from invenio_explicit_acls.utils import AllowedSchemaMixin, \
    convert_relative_schema_to_absolute


class SchemaKeepingRecordMixin(AllowedSchemaMixin):
    """
    A mixin for Record class that makes sure $schema is always in allowed schemas.

    Note that this mixin is not enough, always use invenio_explicit_acls.marshmallow.SchemaEnforcingMixin
    as well. The reason is that Invenio does not inject custom Record implementation for PUT, PATCH and DELETE
    operations.
    """

    # DO NOT forget to set these up in subclasses
    ALLOWED_SCHEMAS = ()
    PREFERRED_SCHEMA = None
    _RESOLVED = False

    def clear(self):
        """Preserves the schema even if the record is cleared and all metadata wiped out."""
        schema = self.get('$schema')
        super().clear()
        if schema:
            self['$schema'] = schema

    def update(self, e=None, **f):
        """Dictionary update."""
        self._check_schema(e or f)
        return super().update(e, **f)

    @classmethod
    def _check_schema(cls, data):
        schema = cls._convert_and_get_schema(data)
        if schema:
            if schema not in cls.ALLOWED_SCHEMAS:
                raise AttributeError('Schema %s not in allowed schemas %s' % (data['$schema'], cls.ALLOWED_SCHEMAS))

    def __setitem__(self, key, value):
        """Dict's setitem."""
        if key == '$schema':
            self._prepare_schemas()
            if value not in self.ALLOWED_SCHEMAS:
                value = current_jsonschemas.path_to_url(value)
                if value not in self.ALLOWED_SCHEMAS:
                    raise AttributeError('Schema %s not in allowed schemas %s' % (value, self.ALLOWED_SCHEMAS))
            value = convert_relative_schema_to_absolute(value)
        return super().__setitem__(key, value)

    def __delitem__(self, key):
        """Dict's delitem."""
        if key == '$schema':
            raise AttributeError('Schema can not be deleted')

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """
        Creates a new record instance and store it in the database.

        For parameters see :py:class:invenio_records.api.Record
        """
        cls._prepare_schemas()

        if '$schema' not in data:
            data['$schema'] = convert_relative_schema_to_absolute(cls.PREFERRED_SCHEMA)
        else:
            cls._check_schema(data)
        ret = super().create(data, id_, **kwargs)
        return ret


class SchemaEnforcingRecord(SchemaKeepingRecordMixin, Record):
    """Sample implementation of Record for the cookiecutter records datamodel."""

    ALLOWED_SCHEMAS = ('records/record-v1.0.0.json',)
    PREFERRED_SCHEMA = 'records/record-v1.0.0.json'
