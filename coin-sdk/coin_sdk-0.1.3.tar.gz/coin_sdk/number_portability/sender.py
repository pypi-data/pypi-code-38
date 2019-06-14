import logging

import requests

from coin_sdk.number_portability.config import Config
from coin_sdk.number_portability.domain import MessageType
from coin_sdk.number_portability.messages.message_response import MessageResponse
from coin_sdk.number_portability.securityservice import SecurityService
from coin_sdk.number_portability.utils import json2obj, handle_http_error

logger = logging.getLogger(__name__)


def _send_request(request, url, json, security_service):
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
    try:
        return MessageResponse(response_json.transaction_id)
    except AttributeError:
        return response_json


class Sender:
    def __init__(self, config: Config):
        self._security_service = SecurityService(config)
        self._config = config

    def send_message(self, message):
        logger.info(f'Sending message: {message}')
        message_type = message.get_message_type()
        message_dict = message.to_dict()
        url = f'{self._config.api_url}/{message_type.value}'
        logger.debug(f'url: {url}')
        return _send_request(requests.post, url, message_dict, self._security_service)

    def confirm(self, transaction_id):
        logger.info(f'Sending conformation for id: {transaction_id}')
        url = f'{self._config.api_url}/{MessageType.CONFIRMATION_V1.value}/{transaction_id}'
        logger.debug(f'url: {url}')
        json = {'transactionId': transaction_id}
        return _send_request(requests.put, url, json, self._security_service)
