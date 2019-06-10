#
# Copyright (c) 2019 UCT Prague.
# 
# marshmallow.py is part of Invenio Explicit ACLs 
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
"""Marshmallow mixin that returns cached ACLs on Record."""
from marshmallow import ValidationError, fields, post_load, validates

from invenio_explicit_acls.utils import AllowedSchemaMixin, \
    convert_relative_schema_to_absolute


class SchemaEnforcingMixin(AllowedSchemaMixin):
    """A marshmallow mixin that enforces that record has only one of predefined schemas."""

    ALLOWED_SCHEMAS = ('records/record-v1.0.0.json',)
    """A list of allowed schemas, either relative or absolute urls."""

    PREFERRED_SCHEMA = 'records/record-v1.0.0.json'
    """If a schema is not set, add this schema."""

    schema = fields.String(attribute='$schema', load_from='$schema', dump_to='$schema', required=False)

    @validates('schema')
    def validate_schema(self, value):
        """Checks that schema (if provided) is in the list of allowed schemas."""
        self._prepare_schemas()
        value = convert_relative_schema_to_absolute(value)
        if value:
            if value not in self.ALLOWED_SCHEMAS:
                raise ValidationError('Schema %s not in allowed schemas %s' % (value, self.ALLOWED_SCHEMAS))

    @post_load
    def add_schema(self, data):
        """If schema has not been provided, sets the PREFERRED_SCHEMA."""
        self._prepare_schemas()
        if '$schema' not in data:
            data['$schema'] = convert_relative_schema_to_absolute(self.PREFERRED_SCHEMA)
        else:
            self._convert_and_get_schema(data)
        return data


class ACLRecordSchemaMixinV1(object):
    """Mixin for returning ACLs."""

    invenio_explicit_acls = fields.Dict(dump_only=True)
