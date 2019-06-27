import logging
import sys

from .exceptions import Http404
from . import responses, serializers, contentnegotiation


log = logging.getLogger(__name__)


class DefaultResourceDispatcher(object):
    def __init__(self, resource):
        self.resource = resource

    def dispatch(self, ctx, args=None, kwargs=None):
        resource = self.resource
        method = ctx.method

        # support for X-HTTP-METHOD-OVERRIDE

        method = ctx.headers.get('x-http-method-override') or method

        # Check request method and raise MethodNotAllowed if unsupported

        allowed_methods = resource.get_allowed_methods()

        if method not in allowed_methods:
            headers = {
                    'Allow': ', '.join(allowed_methods),
                }
            return ctx.MethodNotAllowed({
                'error': 'Method `%s` is not registered for resource `%s`' % (
                    method, resource._path)}, headers=headers)

        # Negotiate payload content type and store the best matching
        # result in ctx.request_content_type

        if ctx.content_type and ctx.content_length:
            media_types = resource.get_method_supported_mediatypes(method)
            if media_types:
                ctx.request_content_type = contentnegotiation.best_match(
                        media_types, ctx.content_type)
            else:
                # server does not support any representation
                ctx.request_content_type = None
        elif ctx.content_length:
            # No payload content-type was provided.
            # According to RFC7231 (Section 3.1.1.5) server may assume
            # "application/octet-stream" or try to examine the type.

            ctx.request_content_type = 'application/octet-stream'
        else:
            # No payload
            ctx.request_content_type = None

        # match response representation, serializer and content type

        if ctx.content_length and ctx.content_type:
            if ctx.request_content_type:
                if ctx.raw:
                    try:
                        ctx.validator = resource._validators[
                                    ctx.request_content_type]
                    except KeyError:
                        pass
                    else:
                        try:
                            ctx.body = ctx.validator.parse(ctx)
                        except serializers.DeserializationError as ex:
                            resp = responses.exception_response_factory(
                                    ctx, ex, cls=responses.BadRequestResponse)
                            return resp
            elif not ctx.content_length:
                ctx.body = None
            else:
                return ctx.UnsupportedMediaType()

        log.debug('Calling %s, %s, %s' % (method, args, kwargs))

        try:
            callback = resource.get_callback(method, ctx.request_content_type)
            resp = self.do_call(callback, ctx, args=args, kwargs=kwargs)
        except Http404:
            return ctx.NotFound()
        except Exception as ex:
            if resource._api.debug:
                tb = sys.exc_info()[2]
            else:
                tb = None
            resp = responses.exception_response_factory(ctx, ex, tb)
            log.exception(
                    'Internal Server Error: %s', ctx.request.path,
                    exc_info=sys.exc_info(),
                    extra={
                        'status_code': resp.status,
                        'context': ctx,
                    }
            )
            return resp
        else:
            if not resp:
                raise TypeError(
                        'Function `%s` does not return '
                        'a response object' % callback)
            return resp

    def do_call(self, callback, ctx, args=None, kwargs=None):
        return callback(ctx, *args, **kwargs)


def resource_dispatcher_factory(
        api, resource, response_builder, context_builder,
        dispatcher_class=DefaultResourceDispatcher):

    dispatcher = dispatcher_class(resource)

    def dispatch_request(request, *args, **kw):
        ctx = context_builder(api, resource, request)
        bypass_processing = False
        middlewares_called = []

        for middleware in api.middlewares:
            middlewares_called.append(middleware)

            try:
                method = middleware.process_request
            except AttributeError:
                pass
            else:
                response = method(request, ctx)
                if response:
                    bypass_processing = True
                    break

        if not bypass_processing:
            response = dispatcher.dispatch(ctx, args=args, kwargs=kw)

        response = response or None

        for middleware in reversed(api.middlewares):
            try:
                method = middleware.process_response
            except AttributeError:
                pass
            else:
                new_response = method(request, response, ctx)
                if new_response:
                    response = new_response

        response = resource._http_response(response)
        return response_builder(response)
    return dispatch_request
