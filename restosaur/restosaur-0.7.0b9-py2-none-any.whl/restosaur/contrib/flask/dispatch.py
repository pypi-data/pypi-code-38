import flask
import functools

from restosaur.headers import normalize_header_name
from restosaur.urltemplate import RE_PARAMS
from restosaur.dispatch import resource_dispatcher_factory


def to_flask_pattern(path):
    return RE_PARAMS.sub('/<\\2>', path)


def build_context(api, resource, request):
    is_secure = request.url.startswith('https')
    headers = dict(map(
            lambda x: (normalize_header_name(x[0]), x[1]),
            request.headers.items()))

    return api.make_context(
            host=request.host, path=request.path,
            method=request.method, parameters=request.args,
            data=request.data, files=request.files, raw=request.get_data(),
            charset=request.charset or api.default_charset,
            secure=is_secure, encoding=request.charset,
            resource=resource, request=request, headers=headers,
            content_type=request.content_type,
            content_length=request.content_length)


def build_http_response(app, response):
    if response is None:
        return flask.Response()
    else:
        if response.serializer:
            content = response.serializer.dumps(response.content)
        else:
            content = ''

        http_resp = app.make_response(
                (content, response.status, response.headers))
        http_resp.headers['Content-Type'] = response.content_type
        return http_resp


def register_api(api, app):
    """
    Bind the `api` instance to the Flask `app` application
    """

    api.debug = app.config['DEBUG']

    for resource in api.resources:
        path = api.path+to_flask_pattern(resource._path)

        if not path.startswith('/'):
            path = '/'+path

        dispatcher = resource_dispatcher_factory(
                api, resource, functools.partial(build_http_response, app),
                context_builder=build_context)

        endpoint = 'restosaour_resource_%s' % id(resource)

        app.add_url_rule(
                path, endpoint=endpoint,
                view_func=functools.partial(dispatcher, flask.request),
                methods=resource.get_allowed_methods())
