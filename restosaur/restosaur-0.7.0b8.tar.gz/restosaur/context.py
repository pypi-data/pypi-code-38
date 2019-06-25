import email
import functools
import six
import times

from .datastructures import QueryDict

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


from .loading import load_resource
from .representations import match_representation
from .utils import force_bytes
from . import responses


def parse_http_date(header, headers):
    if header in headers and headers[header]:
        timetuple = email.utils.parsedate_tz(headers[header])
        try:
            return times.from_unix(email.utils.mktime_tz(timetuple))
        except (TypeError, ValueError):
            pass


class Context(object):
    def __init__(
            self, api, host='localhost', path='/', method='GET',
            parameters=None, body=None, data=None, files=None, raw=None,
            extra=None, headers=None, charset=None, secure=False,
            encoding='utf-8', resource=None, request=None, content_length=None,
            content_type=None):
        self.method = method
        self.api = api
        self.charset = charset
        self.headers = headers or {}
        self.resource = resource
        self.request = request
        self.encoding = encoding
        self.secure = secure
        self.host = host
        self.path = path
        self.body = body
        self.raw = raw
        self.parameters = QueryDict(parameters)  # GET
        self.data = data or {}  # POST
        self.files = files or {}  # FILES
        self.deserializer = None
        self.content_type = content_type
        self.content_length = content_length
        self.extra = extra or {}

    def build_absolute_uri(self, path=None, parameters=None):
        """
        Returns absolute uri to the specified `path` with optional
        query string `parameters`.

        If no `path` is provided, the current request full path
        (including query string) will be used and extended by
        optional `parameters`.
        """

        def build_uri(path):
            current = 'http%s://%s%s' % (
                    's' if self.secure else '', self.host, self.path)
            return urlparse.urljoin(current, path)

        params = QueryDict()
        if path:
            full_path = u'/'.join(
                    filter(None, (self.api.path+path).split('/')))
            if path.endswith('/'):
                full_path += '/'
            uri = build_uri('/'+full_path)
        else:
            params.update(self.parameters.items())
            uri = build_uri(self.path)

        # todo: change to internal restosaur settings
        enc = self.encoding

        params.update(parameters or {})
        params = list(map(
                lambda x: (x[0], force_bytes(x[1], enc)),
                params.items()))

        if params:
            return '%s?%s' % (uri, urlencode(params))
        else:
            return uri

    def match_representation(self, model):
        return match_representation(self.resource, self, model)

    def transform_representation(self, model):
        representation = self.match_representation(model)
        return representation._transform_func(model, self)

    def url(
            self, model=None, resource=None, name=None,
            parameters=None, query=None):
        """
        Create URL for model named link or resource
        with optional query parameters
        """

        if model and resource:
            raise ValueError('Provide `model` or `resource`. Both set.')

        if model:
            return self.model_url(
                    model, name=name, parameters=parameters, query=query)

        if name:
            raise ValueError("Named link must be used with model")

        if not resource:
            raise ValueError("Resource or model must is required")

        return self.resource_url(
                resource, parameters=parameters, query=query)

    def self_url(self, query=None, append_query=False):
        """
        Create URL pointing to self with optional query parameters.

        If `append_query` is True, the current query string parameters
        will be added.
        """

        return self.resource.uri(self, query=query, append_query=append_query)

    def url_for(self, resource, **kwargs):
        """
        Deprecated resource URL generator
        """
        return self.resource_url(resource, parameters=kwargs)

    def model_url(self, model, name=None, query=None, parameters=None):
        """
        Generate URL for model's named link with optional query parameters.
        Model instance or class is accepted.

        For classes you may use `parameters` argument to provide values
        for path template.
        """
        return self.api.linked_url(
                self, model, name=name, parameters=parameters, query=query)

    def resource_url(self, resource, parameters=None, query=None):
        """
        Generate URL for the resource using path parameters
        and optional query string parameters.
        """

        if isinstance(resource, six.string_types):
            resource = load_resource(resource)
        return resource.uri(self, params=parameters, query=query)

    def is_modified_since(self, dt):
        """
        Compares datetime `dt` with `If-Modified-Since` header value.
        Returns True if `dt` is newer than `If-Modified-Since`,
        False otherwise.
        """
        if_modified_since = parse_http_date('if-modified-since', self.headers)

        if if_modified_since:
            return times.to_unix(
                dt.replace(microsecond=0)) > times.to_unix(if_modified_since)

        return True

    @property
    def deserialized(self):
        return self.body

    def wrap(self, func):
        """Wrap `func` with the Context instance as a last argument"""

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            args = list(args)+[self]
            return func(*args, **kwargs)
        return wrapped

    # response factories

    def Continue(self, *args, **kwargs):  # 100
        return responses.ContinueResponse(self, *args, **kwargs)

    def OK(self, *args, **kwargs):  # 200
        return responses.OKResponse(self, *args, **kwargs)

    def Response(self, *args, **kwargs):  # deprecated 200-like response
        return self.OK(*args, **kwargs)

    def Created(self, *args, **kwargs):  # 201
        return responses.CreatedResponse(self, *args, **kwargs)

    def Accepted(self, *args, **kwargs):  # 202
        return responses.AcceptedResponse(self, *args, **kwargs)

    def NoContent(self, *args, **kwargs):  # 204
        return responses.NoContentResponse(self, *args, **kwargs)

    def MovedPermanently(self, *args, **kwargs):  # 301
        return responses.MovedPermanentlyResponse(self, *args, **kwargs)

    def Found(self, *args, **kwargs):  # 302
        return responses.FoundResponse(self, *args, **kwargs)

    def SeeOther(self, *args, **kwargs):  # 303
        return responses.SeeOtherResponse(self, *args, **kwargs)

    def NotModified(self, *args, **kwargs):  # 304
        return responses.NotModifiedResponse(self, *args, **kwargs)

    def BadRequest(self, *args, **kwargs):  # 400
        return responses.BadRequestResponse(self, *args, **kwargs)

    def Unauthorized(self, *args, **kwargs):  # 401
        return responses.UnauthorizedResponse(self, *args, **kwargs)

    def Forbidden(self, *args, **kwargs):  # 403
        return responses.ForbiddenResponse(self, *args, **kwargs)

    def NotFound(self, *args, **kwargs):  # 404
        return responses.NotFoundResponse(self, *args, **kwargs)

    def MethodNotAllowed(self, *args, **kwargs):  # 405
        return responses.MethodNotAllowedResponse(self, *args, **kwargs)

    def NotAcceptable(self, *args, **kwargs):  # 406
        return responses.NotAcceptableResponse(self, *args, **kwargs)

    def Conflict(self, *args, **kwargs):  # 409
        return responses.ConflictResponse(self, *args, **kwargs)

    def Gone(self, *args, **kwargs):  # 410
        return responses.GoneResponse(self, *args, **kwargs)

    def UnsupportedMediaType(self, *args, **kwargs):  # 415
        return responses.UnsupportedMediaTypeResponse(self, *args, **kwargs)

    def ValidationError(self, *args, **kwargs):  # 422 WEBDAV Deprecated
        return responses.ValidationErrorResponse(self, *args, **kwargs)

    def InternalServerError(self, *args, **kwargs):
        return responses.InternalErrorResponse(self, *args, **kwargs)
    InternalError = InternalServerError

    def Entity(self, *args, **kwargs):  # deprecated, 200
        return responses.EntityResponse(self, *args, **kwargs)

    def Collection(self, *args, **kwargs):  # deprecated, 200
        return responses.CollectionResponse(self, *args, **kwargs)
