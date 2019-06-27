from django.http import HttpResponse, Http404

from restosaur.context import QueryDict
from restosaur.headers import normalize_header_name
from restosaur import dispatch as restosaur_dispatch
from restosaur.exceptions import Http404 as RestosaurHttp404


def build_context(api, resource, request):
    try:
        # Django may raise RawPostDataException sometimes;
        # i.e. when processing POST multipart/form-data;
        # In that cases we can't access raw body anymore, sorry

        raw_body = request.body
    except Exception:
        raw_body = None

    parameters = {}

    if request.resolver_match:
        parameters.update(request.resolver_match.kwargs)

    parameters.update(QueryDict(list(request.GET.lists())))

    headers = dict(map(
        lambda x: (normalize_header_name(x[0]), x[1]),
        filter(lambda x: x[0].startswith('HTTP_'), request.META.items())))

    try:
        content_length = int(request.META['CONTENT_LENGTH'])
    except (KeyError, TypeError, ValueError):
        content_length = 0

    content_type = request.META.get('CONTENT_TYPE')

    return api.make_context(
            host=request.get_host(), path=request.path,
            method=request.method, parameters=parameters,
            data=request.POST, files=request.FILES, raw=raw_body,
            charset=request.encoding or api.default_charset,
            secure=request.is_secure(), encoding=request.GET.encoding,
            resource=resource, request=request, headers=headers,
            content_type=content_type, content_length=content_length)


def http_response_builder(response):
    if response is None:
        return HttpResponse()

    if isinstance(response, HttpResponse):
        return response

    if response.serializer:
        content = response.serializer.dumps(response.context, response.content)
    else:
        content = ''

    httpresp = HttpResponse(content, status=response.status)

    if response.content_type:
        httpresp['Content-Type'] = response.content_type

    for header, value in response.headers.items():
        httpresp[header] = value

    return httpresp


class DjangoMethodDispatcher(restosaur_dispatch.DefaultResourceDispatcher):
    def do_call(self, callback, ctx, args=None, kwargs=None):
        try:
            return super(DjangoMethodDispatcher, self).do_call(
                    callback, ctx, args=args, kwargs=kwargs)
        except Http404 as ex:
            raise RestosaurHttp404(ex)


def resource_dispatcher_factory(api, resource):
    return restosaur_dispatch.resource_dispatcher_factory(
                api, resource, http_response_builder, build_context,
                dispatcher_class=DjangoMethodDispatcher)
