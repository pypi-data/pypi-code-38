# Copyright © 2018-2019 Roel van der Goot
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
"""Module query deals with everything related to query parameters."""

from re import compile as re_compile

from ajsonapi.errors import (
    FieldsInvalidFieldError,
    FieldsInvalidResourceError,
    QueryParameterUnsupportedError,
)
from ajsonapi.field import Field

RE_FIELDS = re_compile(r'fields\[([^\]]*)\]')


def query_has_parameter(query, name):
    """Checks if a query parameter exists."""
    for parameter in query:
        if parameter.split('[')[0] == name:
            return True
    return False


def parse_fields(request_query, query, errors, *, allow=False):
    """Parses the request's fields query parameter."""

    if query_has_parameter(request_query, 'fields'):
        if allow:
            query['fields'] = fields_dict(request_query, errors)
        else:
            errors.append(QueryParameterUnsupportedError('fields'))
    else:
        query['fields'] = {}


def fields_dict(request_query, errors):
    """Helper function for parsing request query fields parameters."""

    from ajsonapi.uri.collection import Collection

    return_dict = {}
    for key, values in request_query.items():
        match = RE_FIELDS.match(key)
        if match:
            collection_name = match.group(1)
            try:
                collection = Collection.by_name[collection_name]
            except KeyError:
                errors.append(FieldsInvalidResourceError(collection_name))
                continue
            return_dict[collection] = []
            if values == '':
                continue
            for field_name in values.split(','):
                try:
                    field = getattr(collection.table, field_name)
                except AttributeError:
                    errors.append(
                        FieldsInvalidFieldError(collection_name, field_name))
                    continue
                if not isinstance(field, Field):
                    errors.append(
                        FieldsInvalidFieldError(collection_name, field_name))
                else:
                    return_dict[collection].append(field)
    return return_dict


def parse_sort(request_query, query, errors):
    """Parses the request's sort query parameter."""
    if query_has_parameter(request_query, 'sort'):
        errors.append(QueryParameterUnsupportedError('sort'))
    query['sort'] = lambda x: True


def parse_page(request_query, query, errors):
    """Parses the request's page query parameter."""
    if query_has_parameter(request_query, 'page'):
        errors.append(QueryParameterUnsupportedError('page'))
    query['page'] = None
