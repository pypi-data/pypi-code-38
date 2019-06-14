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
"""Module errors provides errors related to request parsing."""

from abc import ABC, abstractmethod


class Error(ABC):
    """Abstract base class for all JSON API errors."""

    # pylint: disable=too-few-public-methods

    @abstractmethod
    def to_error(self):
        """Returns a JSON API error document for use in the response
        document's errors array.
        """


class MethodNotAllowedError(Error):
    """Method not allowed for URL."""

    # pylint: disable=too-few-public-methods

    status = 405

    def to_error(self):
        return {
            'status': '405',
            'title': 'Method not allowed.',
        }


class ResourceNotFoundError(Error):
    """Errors related to an invalid url in a request."""

    # pylint: disable=too-few-public-methods

    status = 404

    def __init__(self, path, about=None):
        self.path = path
        self.about = about

    def to_error(self):
        return {
            'status': '404',
            'source': {
                'path': self.path,
            },
            'title': 'Resource does not exist.',
        }


class ResourceNotFoundMalformedIdError(Error):
    """Errors related to an invalid url due to a malformed id in a request."""

    # pylint: disable=too-few-public-methods

    status = 404

    def __init__(self, path, about=None):
        self.path = path
        self.about = about

    def to_error(self):
        return {
            'status': '404',
            'source': {
                'path': self.path,
            },
            'title': 'Resource does not exist.',
            'detail': 'Malformed id.',
        }


class QueryParameterUnsupportedError(Error):
    """Errors related to unsupported query parameters in a request."""

    # pylint: disable=too-few-public-methods

    status = 400

    def __init__(self, parameter, about=None):
        self.parameter = parameter
        self.about = about

    def to_error(self):
        return {
            'status': '400',
            'source': {
                'parameter': self.parameter,
            },
            'title': 'Parameter not supported.',
        }


class IncludeInvalidPathError(Error):
    """Errors related to an invalid include relationship path."""

    # pylint: disable=too-few-public-methods

    status = 400

    def __init__(self, path):
        self.path = path

    def to_error(self):
        return {
            'status':
            '400',
            'source': {
                'parameter': 'include'
            },
            'title':
            'Invalid query parameter.',
            'detail': ("The resource does not have a "
                       f"'{self.path}' relationship path.")
        }


class FieldsInvalidResourceError(Error):
    """Errors related to an invalid fields resource."""

    # pylint: disable=too-few-public-methods

    status = 400

    def __init__(self, resource):
        self.resource = resource

    def to_error(self):
        return {
            'status': '400',
            'source': {
                'parameter': 'fields'
            },
            'title': 'Invalid query parameter.',
            'detail': f"Resource '{self.resource}' does not exist."
        }


class FieldsInvalidFieldError(Error):
    """Errors related to an invalid fields field."""

    # pylint: disable=too-few-public-methods

    status = 400

    def __init__(self, resource, field):
        self.resource = resource
        self.field = field

    def to_error(self):
        return {
            'status':
            '400',
            'source': {
                'parameter': 'fields'
            },
            'title':
            'Invalid query parameter.',
            'detail': (f"Field '{self.field}' does not exist in resource "
                       f"'{self.resource}'.")
        }


class FilterInvalidFieldError(Error):
    """Errors related to an invalid filter field."""

    # pylint: disable=too-few-public-methods

    status = 400

    def __init__(self, path):
        self.path = path

    def to_error(self):
        return {
            'status': '400',
            'source': {
                'parameter': 'filter'
            },
            'title': 'Invalid query parameter.',
            'detail': f"The resource does not have a '{self.path}' field."
        }


class SortInvalidFieldError(Error):
    """Errors related to an invalid sort field."""

    # pylint: disable=too-few-public-methods

    status = 400

    def __init__(self, path):
        self.path = path

    def to_error(self):
        return {
            'status': '400',
            'source': {
                'parameter': 'sort'
            },
            'title': 'Invalid query parameter.',
            'detail': f"The resource does not have a '{self.path}' field."
        }


class UnsupportedMediaTypeError(Error):
    """Error in response to a request with a Content-Type header that
    specifies the JSON API media type ('application/vnd.api+json') with any
    media type parameter.
    """

    # pylint: disable=too-few-public-methods

    status = 415

    def to_error(self):
        return {
            'status': '415',
            'source': {
                'header': 'Content-Type',
            },
            'title': 'Invalid header.',
        }


class NotAcceptableError(Error):
    """Error in response to a request with an Accept header that only have
    media type parameters specified when the media type in JSON API
    ('application/vnd.api+json').
    """

    # pylint: disable=too-few-public-methods

    status = 406

    def to_error(self):
        return {
            'status': '406',
            'source': {
                'header': 'Accept',
            },
            'title': 'Invalid header.',
        }


class DocumentNotJsonError(Error):
    """Error in response to a request with a document that is not JSON."""

    # pylint: disable=too-few-public-methods

    status = 400

    def to_error(self):
        return {
            'status': '400',
            'title': 'Invalid document.',
            'detail': 'Document is not JSON.',
        }


class DocumentDataMissingError(Error):
    """Error in response to a request with a document that is missing a
    top-level data member.
    """

    # pylint: disable=too-few-public-methods

    status = 422

    def to_error(self):
        return {
            'status': '422',
            'source': {
                'pointer': '',
            },
            'title': 'Invalid document.',
            'detail': "Missing 'data' member at document's top level.",
        }


class DocumentError(Error, ABC):
    """Error in response to a request with a document error."""

    # pylint: disable=too-few-public-methods

    status = 422

    def __init__(self, pointer):
        super().__init__()
        self.pointer = pointer

    @abstractmethod
    def to_error(self):
        pass


class DocumentDataMalformedUuidError(DocumentError):
    """Error in response to a POST /{collection} request where the request's
    document contains a resource object with an id that is not a
    client-generated id (UUID).
    """

    # pylint: disable=too-few-public-methods

    def to_error(self):
        return {
            'status': '422',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource object.',
            'detail': 'Malformed client-generated id.',
        }


class DocumentDataInvalidAttributeError(DocumentError):
    """Error in response to a POST /{collection} request where the request's
    document contains a resource object with an invalid attribute.
    """

    # pylint: disable=too-few-public-methods

    def to_error(self):
        return {
            'status': '422',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource object.',
            'detail': 'Invalid attribute.',
        }


class DocumentDataInvalidRelationshipError(DocumentError):
    """Error in response to a POST /{collection} request where the request's
    document contains a resource object with an invalid relationship.
    """

    # pylint: disable=too-few-public-methods

    def to_error(self):
        return {
            'status': '422',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource object.',
            'detail': 'Invalid relationship.',
        }


class DocumentDataMissingTypeError(DocumentError):
    """Error in response to a POST /{collection} or a PATCH /{collection/{id}
    request where the request's document contains a resource object without a
    type.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, pointer='/data'):
        super().__init__(pointer)

    def to_error(self):
        return {
            'status': '422',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource object.',
            'detail': 'Missing type.',
        }


class DocumentDataMissingIdError(DocumentError):
    """Error in response to a PATCH /{collection/{id} request where the
    request document contains a resource object without an id.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, pointer='/data'):
        super().__init__(pointer)

    def to_error(self):
        return {
            'status': '422',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource object.',
            'detail': 'Missing id.',
        }


class DocumentDataNonexistentIdError(DocumentError):
    """Error in response to a PATCH
    /{collection}/{id}/relationships/{relationship} request where the request
    document contains a resource object with an id that does not exist.
    """

    # pylint: disable=too-few-public-methods

    def to_error(self):
        return {
            'status': '422',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource identifier object.',
            'detail': 'Nonexistent id.',
        }


class DocumentDataRelationshipConflictError(DocumentError):
    """Error in response to a PATCH
    /{collection}/{id}/relationships/{relationship} request where the request
    document contains a resource identifier object that is part of another
    one-to-one relationship already.
    """

    # pylint: disable=too-few-public-methods

    status = 409

    def __init__(self):
        super().__init__('/data')

    def to_error(self):
        return {
            'status':
            '409',
            'source': {
                'pointer': self.pointer,
            },
            'title':
            'Conflicting resource identifier object.',
            'detail':
            'Resource identifier object is part of another '
            'one-to-one relationship.',
        }


class DocumentDataMalformedError(Error):
    """This error indicates that the request's document contains a malformed
    data member.
    """

    # pylint: disable=too-few-public-methods

    status = 422

    def to_error(self):
        return {
            'status': '422',
            'source': {
                'pointer': '/data',
            },
            'title': 'Invalid resource object.',
            'detail': "Malformed 'data' member.",
        }


class DocumentDataInvalidTypeError(DocumentError):
    """Error in response to a POST /{collection} or PATCH /{collection}/{id}
    request where the request's document contains a resource object with an
    invalid type.
    """

    # pylint: disable=too-few-public-methods

    status = 409

    def to_error(self):
        return {
            'status': '409',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource object.',
            'detail': 'Invalid type.',
        }


class DocumentDataDuplicateIdError(DocumentError):
    """Error in response to a POST /{collection} request where the request's
    document contains an id that already exists so the resource object annot
    be created.
    """

    # pylint: disable=too-few-public-methods

    status = 409

    def to_error(self):
        return {
            'status': '409',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource object.',
            'detail': 'Id already exists.',
        }


class DocumentDataInvalidIdError(DocumentError):
    """Error in response to PATCH /{collection}/id request where the request
    document contains a resource object with an invalid id.
    """

    # pylint: disable=too-few-public-methods

    status = 409

    def __init__(self, title, pointer):
        super().__init__(pointer)
        self.title = title

    def to_error(self):
        return {
            'status': '409',
            'source': {
                'pointer': self.pointer,
            },
            'title': self.title,
            'detail': 'Invalid id.',
        }


class DocumentDataMalformedIdError(DocumentError):
    """Error in response to PATCH /{collection}/id request where the request
    document contains a resource object with a malformed id.
    """

    # pylint: disable=too-few-public-methods

    status = 409

    def __init__(self, title, pointer):
        super().__init__(pointer)
        self.title = title

    def to_error(self):
        return {
            'status': '409',
            'source': {
                'pointer': self.pointer,
            },
            'title': self.title,
            'detail': 'Malformed id.',
        }


class DocumentDataMissingRelationshipTypeError(DocumentError):
    """Error in response to a POST /{collection} or a PATCH /{collection/{id}
    request where the request's document contains a resource object with a
    relationship without a type.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, pointer='/data'):
        super().__init__(pointer)

    def to_error(self):
        return {
            'status': '422',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource object.',
            'detail': 'Missing relationship type.',
        }


class DocumentDataInvalidRelationshipTypeError(DocumentError):
    """Error in response to a POST /{collection} or PATCH /{collection}/{id}
    request where the request's document contains a resource object with a
    relationship with an invalid type.
    """

    # pylint: disable=too-few-public-methods

    status = 409

    def to_error(self):
        return {
            'status': '409',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource object.',
            'detail': 'Invalid relationship type.',
        }


class DocumentDataMissingRelationshipIdError(DocumentError):
    """Error in response to a POST /{collection} or PATCH /{collection/{id}
    request where the request document contains a resource object with a
    relationship without an id.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, pointer='/data'):
        super().__init__(pointer)

    def to_error(self):
        return {
            'status': '422',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource object.',
            'detail': 'Missing relationship id.',
        }


class DocumentDataMalformedRelationshipIdError(DocumentError):
    """Error in response to POST /{collection} or PATCH /{collection}/id
    request where the request document contains a resource object with a
    malformed id.
    """

    # pylint: disable=too-few-public-methods

    status = 409

    def __init__(self, title, pointer):
        super().__init__(pointer)
        self.title = title

    def to_error(self):
        return {
            'status': '409',
            'source': {
                'pointer': self.pointer,
            },
            'title': self.title,
            'detail': 'Malformed relationship id.',
        }


class DocumentDataMalformedRelationshipError(DocumentError):
    """This error indicates that a request's document contains a malformed
    relationship.
    """

    # pylint: disable=too-few-public-methods

    status = 422

    def to_error(self):
        return {
            'status': '422',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource object.',
            'detail': 'Malformed relationship.',
        }


class DocumentDataMalformedRelationshipDataError(DocumentError):
    """This error indicates that a request's document contains a relationship
    whose data member is malformed.
    """

    # pylint: disable=too-few-public-methods

    status = 422

    def to_error(self):
        return {
            'status': '422',
            'source': {
                'pointer': self.pointer,
            },
            'title': 'Invalid resource object.',
            'detail': 'Malformed relationship data.',
        }


class DeleteObjectRemotelyRelatedError(Error):
    """This error indicates that the DELETE request of a resource object
    failed due to the resource object having an active remote relationship.
    """

    # pylint: disable=too-few-public-methods

    status = 409

    def __init__(self, path):
        self.path = path

    def to_error(self):
        return {
            'status': '409',
            'source': {
                'path': self.path,
            },
            'title': 'Cannot delete a remotely related resource object.',
        }
