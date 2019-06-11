import functools
import os
import opentracing

from . import utils

def wrapper(func):
    @functools.wraps(func)
    def call(*args, **kwargs):
        print(args)
        print(kwargs)
        print("tracing wrapper")
        set_tracer(args[1])
        tracer = opentracing.tracer

        tags = utils.get_fields(args[1])

        try:
            with opentracing.tracer.start_active_span('tracing_wrapper', tags=tags) as scope:

                # do nothing else for now
                value = func(*args, **kwargs)
                print(value)
                return value
        except BaseException as e:
            print("exception")
            scope.span.set_tag('error', True)
            scope.span.log_kv({'error.object': e})
            raise
        finally:
            print("flushing")
            opentracing.tracer.close()

    return call


def set_tracer(context):
    from jaeger_client import Config
    from jaeger_client import constants

    endpoint = os.getenv('SIGNALFX_TRACING_URL', 'https://ingest.signalfx.com/v1/trace')
    service_name = os.getenv('SIGNALFX_SERVICE_NAME', context.function_name)
    access_token = os.getenv('SIGNALFX_AUTH_TOKEN', '')
    print(endpoint)

    config = {
            'sampler': {
                'type': 'const',
                'param': 1
                },
            'propagation': 'b3',
            'jaeger_endpoint': endpoint,
            'jaeger_user': 'auth',
            'jaeger_password': access_token,
            'logging': True,
            }

    tracer_config = Config(config=config, service_name=service_name)

    tracer = tracer_config.initialize_tracer()


