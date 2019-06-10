import logging
import json

from sanic.handlers import ErrorHandler
from jaeger_client import Config
from jaeger_client.metrics.prometheus import PrometheusMetricsFactory

from xintian.exception import CustomException

logger = logging.getLogger('xintian')


def jsonify(records):
    """
    Parse database record response into JSON format
    """
    return [dict(r.items()) for r in records]


class CustomHandler(ErrorHandler):

    def default(self, request, exception):
        if isinstance(exception, CustomException):
            data = {
                'message': exception.message,
                'code': exception.code,
            }
            if exception.error:
                data.update({'error': exception.error})
            return json.dumps(data, status=exception.status_code)
        return super().default(request, exception)


def init_jaeger_tracer(service_name='xintian-app-demo', use_promethus=False):
    if use_promethus:
        config = Config(
            config={},
            service_name=service_name,
            validate=True,
            metrics_factory=PrometheusMetricsFactory(namespace=service_name)
        )
        return config.initialize_tracer()
    else:
        config = Config(config={}, service_name=service_name, validate=True)
        return config.initialize_tracer()
