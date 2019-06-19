import logging
import json
from django.conf import settings

logger = logging.getLogger('apilog')

class LoggingMiddleware(object):
    def __init__(self, get_response):
        # One-time configuration and initialization.
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request._body_to_log = request.body
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response

    @staticmethod
    def process_template_response(request, response):
        config = getattr(settings, 'LINS_RESTAPI_MIDDLEWARE_LOGS', {})
        config_status_ignoradaos = config.get('STATUS_CODE_IGNORADOS', [])
        config_status_grupo = config.get('STATUS_CODE_ATIVO_GRUPO', [400, 500])

        status_code_base = str(response.status_code)[0]
        status_code_base = int(status_code_base)*100

        if response.status_code not in config_status_ignoradaos:
            if status_code_base in config_status_grupo:
                log_data = {}
                log_data['http_method'] = request.method
                log_data['path'] = request.get_full_path()
                log_data['request_body'] = request._body_to_log.decode('utf-8')
                log_data['status_code'] = response.status_code
                log_data['response_body'] = response.rendered_content.decode('utf-8')
                log_data['username'] = request.user.username

                http_headers = {key:value for (key,value) in request.META.items() if 'HTTP_' in key}
                if http_headers:
                    log_data['http_headers'] = http_headers

                json_data = json.dumps(log_data)

                if response.status_code >= 500:
                    logger.error(json_data)
                elif response.status_code == 400:
                    logger.info(json_data)
                elif response.status_code > 400:
                    logger.warning(json_data)
                else:
                    logger.info(json_data)

        return response

