from __future__ import absolute_import

import opentracing
import opentracing.ext.tags as ext
import wrapt

from ..log import logger
from ..singletons import agent, tracer
from ..util import strip_secrets

try:
    import flask

    def before_request_with_instana(*argv, **kwargs):
        try:
            if not agent.can_send():
                return

            rc = flask._request_ctx_stack.top
            env = rc.request.environ
            ctx = None

            if 'HTTP_X_INSTANA_T' in env and 'HTTP_X_INSTANA_S' in env:
                ctx = tracer.extract(opentracing.Format.HTTP_HEADERS, env)

            span = tracer.start_active_span('flask', child_of=ctx).span

            if agent.extra_headers is not None:
                for custom_header in agent.extra_headers:
                    # Headers are available in this format: HTTP_X_CAPTURE_THIS
                    header = ('HTTP_' + custom_header.upper()).replace('-', '_')
                    if header in env:
                        span.set_tag("http.%s" % custom_header, env[header])

            span.set_tag(ext.HTTP_METHOD, rc.request.method)
            if 'PATH_INFO' in env:
                span.set_tag(ext.HTTP_URL, env['PATH_INFO'])
            if 'QUERY_STRING' in env and len(env['QUERY_STRING']):
                scrubbed_params = strip_secrets(env['QUERY_STRING'], agent.secrets_matcher, agent.secrets_list)
                span.set_tag("http.params", scrubbed_params)

            if 'HTTP_HOST' in env:
                span.set_tag("http.host", env['HTTP_HOST'])
        except Exception:
            logger.debug("Flask before_request", exc_info=True)
        finally:
            return None

    def after_request_with_instana(*argv, **kwargs):
        rc = flask._request_ctx_stack.top

        try:
            span = tracer.active_span

            import ipdb; ipdb.set_trace()

            # If we're not tracing, just return
            if span is None:
                return wrapped(*argv, **kwargs)

            response = argv[0]

            if 500 <= response.status_code <= 511:
                span.set_tag("error", True)
                ec = span.tags.get('ec', 0)
                if ec is 0:
                    span.set_tag("ec", ec+1)

            span.set_tag(ext.HTTP_STATUS_CODE, response.status_code)
            response.headers.add('HTTP_X_INSTANA_T', id_to_header(span.context.trace_id))
            response.headers.add('HTTP_X_INSTANA_S', id_to_header(span.context.span_id))
            response.headers.add('HTTP_X_INSTANA_L', 1)
        except Exception:
            logger.debug("Flask after_request", exc_info=True)
        finally:
            return response

    @wrapt.patch_function_wrapper('flask', 'Flask.__init__')
    def init_with_instana(wrapped, instance, args, kwargs):
        rv = wrapped(*args, **kwargs)
        instance.before_request(before_request_with_instana)
        instance.after_request(after_request_with_instana)
        return rv

    logger.debug("Instrumenting flask")
except ImportError:
    pass
