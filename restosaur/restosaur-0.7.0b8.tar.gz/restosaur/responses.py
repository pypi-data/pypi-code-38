import times
import warnings

from email.utils import formatdate

from .representations import ExceptionRepresentation
from .utils import Collection


NOTSET = 'NOTSET'


def dummy_converter(x, context):
    return x


def http_date(x):
    return formatdate(x, usegmt=True)


class StatusCodeMismatch(ValueError):
    def __init__(self, class_name, status_code):
        super(StatusCodeMismatch, self).__init__(
            '%s' % (self.class_name, self.status_code))


class BaseResponse(object):
    def __init__(
            self, context, data=None, status=200, headers=None,
            last_modified=None):

        self.headers = {}

        for key, value in (headers or {}).items():
            self[key] = value

        self.representation = None
        self.content_type = None
        self.context = context
        self._status = status
        self.data = data

        if last_modified:
            self.set_last_modified(last_modified)

    def set_last_modified(self, dt):
        if dt:
            self.headers['Last-Modified'] = http_date(times.to_unix(dt))
        else:
            self.headers.pop('Last-Modified', None)

    @property
    def status(self):
        return self._status

    @status.setter
    def set_status(self, status):
        self._validate_status_code(status)
        self._status = status

    def __setitem__(self, name, value):
        self.headers[name] = value

    def __getitem__(self, name):
        return self.headers[name]

    def _validate_status_code(self, status):
        pass


class InformationalResponse(BaseResponse):
    def _validate_status_code(self, status):
        if status < 100 or status >= 200:
            raise StatusCodeMismatch('Informational', status)


class SuccessfulResponse(BaseResponse):
    def _validate_status_code(self, status):
        if status < 200 or status >= 300:
            raise StatusCodeMismatch('Successful', status)


class RedirectionResponse(BaseResponse):
    def _validate_status_code(self, status):
        if status < 300 or status >= 400:
            raise StatusCodeMismatch('Redirection', status)


class ClientErrorResponse(BaseResponse):
    def _validate_status_code(self, status):
        if status < 400 or status >= 500:
            raise StatusCodeMismatch('ClientError', status)


class ServerErrorResponse(BaseResponse):
    def _validate_status_code(self, status):
        if status < 500 or status >= 600:
            raise StatusCodeMismatch('ServerError', status)


class ContinueResponse(InformationalResponse):
    def __init__(self, context, headers=None):
        super(ContinueResponse, self).__init__(
                context, status=100, headers=headers)


class OKResponse(SuccessfulResponse):
    def __init__(self, context, data=None, headers=None):
        super(OKResponse, self).__init__(
                context, data=data, status=200, headers=headers)


class CreatedResponse(SuccessfulResponse):
    def __init__(self, context, data=None, headers=None):
        super(CreatedResponse, self).__init__(
                context, data=data, status=201, headers=headers)


class AcceptedResponse(SuccessfulResponse):
    def __init__(self, context, data=None, headers=None):
        super(AcceptedResponse, self).__init__(
                context, data=data, status=202, headers=headers)


class NoContentResponse(SuccessfulResponse):
    def __init__(self, context, headers=None):
        # No content/data as stated in RFC7231 (6.3.5)
        super(NoContentResponse, self).__init__(
                context, status=204, headers=headers)


class ResetContentResponse(SuccessfulResponse):
    def __init__(self, context, headers=None):
        # No content/data as stated in RFC7231 (6.3.6)
        super(ResetContentResponse, self).__init__(
                context, status=205, headers=headers)


class MultipleChoicesResponse(RedirectionResponse):
    def __init__(self, context, data=None, headers=None):
        super(MultipleChoicesResponse, self).__init__(
                context, data=data, status=300, headers=headers)


class MovedPermanentlyResponse(RedirectionResponse):
    def __init__(self, context, url, data=None, headers=None):
        headers = headers or {}
        headers['Location'] = url
        super(MovedPermanentlyResponse, self).__init__(
                context, data=data, status=301, headers=headers)


class FoundResponse(RedirectionResponse):
    def __init__(self, context, data=None, headers=None):
        super(FoundResponse, self).__init__(
                context, data=data, status=302, headers=headers)


class SeeOtherResponse(RedirectionResponse):
    def __init__(self, context, url, data=None, headers=None):
        headers = headers or {}
        headers['Location'] = url
        super(SeeOtherResponse, self).__init__(
                context, data=data, status=303, headers=headers)


class NotModifiedResponse(RedirectionResponse):
    def __init__(self, context, data=None, headers=None):
        super(NotModifiedResponse, self).__init__(
                context, data=data, status=304, headers=headers)


class BadRequestResponse(ClientErrorResponse):
    def __init__(self, context, data=None, headers=None):
        super(BadRequestResponse, self).__init__(
                context, data=data, status=400, headers=headers)


class UnauthorizedResponse(ClientErrorResponse):
    def __init__(self, context, data=None, headers=None):
        super(UnauthorizedResponse, self).__init__(
                context, data=data, status=401, headers=headers)


class ForbiddenResponse(ClientErrorResponse):
    def __init__(self, context, data=None, headers=None):
        super(ForbiddenResponse, self).__init__(
                context, data=data, status=403, headers=headers)


class NotFoundResponse(ClientErrorResponse):
    def __init__(self, context, data=None, headers=None):
        super(NotFoundResponse, self).__init__(
                context, data=data, status=404, headers=headers)


class MethodNotAllowedResponse(ClientErrorResponse):
    def __init__(self, context, data=None, headers=None):
        super(MethodNotAllowedResponse, self).__init__(
                context, data=data, status=405, headers=headers)


class NotAcceptableResponse(ClientErrorResponse):
    def __init__(self, context, data=None, headers=None):
        super(NotAcceptableResponse, self).__init__(
                context, data=data, status=406, headers=headers)


class ConflictResponse(ClientErrorResponse):
    def __init__(self, context, data=None, headers=None):
        super(ConflictResponse, self).__init__(
                context, data=data, status=409, headers=headers)


class GoneResponse(ClientErrorResponse):
    def __init__(self, context, data=None, headers=None):
        super(GoneResponse, self).__init__(
                context, data=data, status=410, headers=headers)


class UnsupportedMediaTypeResponse(ClientErrorResponse):
    def __init__(self, context, headers=None):
        super(UnsupportedMediaTypeResponse, self).__init__(
                context, data=None, status=415, headers=headers)


class InternalErrorResponse(ServerErrorResponse):
    def __init__(self, context, data=None, headers=None):
        super(InternalErrorResponse, self).__init__(
                context, data=data, status=500, headers=headers)


class NotImplementedResponse(ServerErrorResponse):
    def __init__(self, context, data=None, headers=None):
        super(NotImplementedResponse, self).__init__(
                context, data=data, status=501, headers=headers)


# deprecated custom responses

class CollectionResponse(SuccessfulResponse):
    def __init__(self, context, iterable, totalCount=None, key=None, **kwargs):
        warnings.warn(
            '`CollectionResponse` will be removed in Restosaur v0.9. '
            'You should use plain `Response` or `OKResponse` '
            '(ctx.Response() / ctx.OK() respectively).',
            DeprecationWarning, stacklevel=3)

        coll_obj = Collection(
                context, iterable, key=key, totalcount=totalCount)
        super(CollectionResponse, self).__init__(
                context, data=coll_obj, **kwargs)


class EntityResponse(OKResponse):
    pass


Response = OKResponse


class ValidationErrorResponse(ClientErrorResponse):
    def __init__(self, context, errors, headers=None):
        resp = {
                'errors': errors,
                }
        super(ValidationErrorResponse, self).__init__(
                context, data=resp, status=422, headers=headers)


def exception_response_factory(context, ex, tb=None, extra=None, cls=None):
    if not cls:
        if isinstance(ex, NotImplementedError):
            cls = NotImplementedResponse
        else:
            cls = InternalErrorResponse

    data = ExceptionRepresentation(ex, tb=tb, extra=extra)
    response = cls(context=context, data=data)
    data.status_code = response.status

    return response
