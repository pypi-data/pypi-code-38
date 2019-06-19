import logging

from coin_sdk.number_portability.utils import json2obj, handle_http_error

logger = logging.getLogger(__name__)


def send_request(request, url, json, security_service):
    method = request.__name__
    headers = security_service.generate_headers(url, method, json)
    cookie = security_service.generate_jwt()
    logger.debug(f'Making request: {method}')
    response = request(url, json=json, headers=headers, cookies=cookie)
    logger.debug(f'Header: {response.request.headers}')
    logger.debug(f'Body: {response.request.body}')
    handle_http_error(response)
    logger.debug('Converting JSON response to Python')
    response_json = json2obj(response.text)
    logger.debug(f'Response: {response_json}')
    return response_json
