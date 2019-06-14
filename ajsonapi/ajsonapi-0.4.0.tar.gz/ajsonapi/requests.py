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
"""Module requests deals with everything related to requests."""

from ajsonapi.document import parse as parse_document
from ajsonapi.headers import parse as parse_headers
from ajsonapi.uri.collection import parse_collection
from ajsonapi.uri.object import parse as parse_object
from ajsonapi.uri.related import parse as parse_related_resource
from ajsonapi.uri.relationship import parse as parse_relationship


def parse_collection_query(request,
                           allow_include=False,
                           allow_fields=False,
                           allow_filter=False,
                           allow_sort=False):
    """Gets the resource collection and query parameters from the request."""

    parse_headers(request)
    collection = parse_collection(request)
    query = collection.parse_query(request,
                                   allow_include=allow_include,
                                   allow_fields=allow_fields,
                                   allow_filter=allow_filter,
                                   allow_sort=allow_sort)
    return collection, query


async def parse_collection_document_query(request, allow_include=False):
    """Gets the resource collection, the data member from the document, and
    query parameters from the request.
    """

    parse_headers(request)
    collection = parse_collection(request)
    query = collection.parse_query(request, allow_include=allow_include)
    data = await parse_document(request)
    return collection, data, query


async def parse_object_query(request, allow_include=False, allow_fields=False):
    """Gets the resource object and query parameters from the request."""

    parse_headers(request)
    object_ = parse_object(request)
    query = object_.collection.parse_query(request,
                                           allow_include=allow_include,
                                           allow_fields=allow_fields)
    return object_, query


async def parse_object_document_query(request):
    """Gets the resource object, the data member from the document, and query
    parameters from the request.
    """

    parse_headers(request)
    object_ = parse_object(request)
    query = object_.collection.parse_query(request)
    data = await parse_document(request)
    return object_, data, query


async def parse_relationship_query(request,
                                   allow_include=False,
                                   allow_fields=False):
    """Gets the relationship and query parameters from the request."""

    parse_headers(request)
    relationship = parse_relationship(request)
    query = relationship.collection.parse_query(request,
                                                allow_include=allow_include,
                                                allow_fields=allow_fields)
    return relationship, query


async def parse_relationship_document_query(request, allow_include=False):
    """Gets the relationship and query parameters from the request."""

    parse_headers(request)
    relationship = parse_relationship(request)
    query = relationship.collection.parse_query(request,
                                                allow_include=allow_include)
    data = await parse_document(request)
    return relationship, data, query


async def parse_related_resource_query(request,
                                       allow_include=False,
                                       allow_fields=False,
                                       allow_filter=False,
                                       allow_sort=False):
    """Gets the related resource and query parameters from the request."""

    parse_headers(request)
    related_resource = parse_related_resource(request)
    query = related_resource.relationship.rtable.collection.parse_query(
        request,
        allow_include=allow_include,
        allow_fields=allow_fields,
        allow_filter=(allow_filter and related_resource.is_to_many()),
        allow_sort=(allow_sort and related_resource.is_to_many()))
    return related_resource, query
