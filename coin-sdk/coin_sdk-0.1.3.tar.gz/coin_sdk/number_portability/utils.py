import json
import logging
from collections import namedtuple
from http import HTTPStatus
from json import JSONDecodeError

import requests

from coin_sdk.number_portability.domain import ConfirmationStatus, MessageType
from coin_sdk.number_portability.messages.common import ErrorMessage
from coin_sdk.number_portability.securityservice import SecurityService

logger = logging.getLogger(__name__)


def _json_object_hook(d):
    return namedtuple('np', d.keys())(*d.values())


def json2obj(data):
    try:
        return json.loads(data, object_hook=_json_object_hook)
    except JSONDecodeError:
        return data


def handle_http_error(response):
    logger.debug('Checking for errors')
    status = response.status_code
    logger.debug(f'Http Status: {status}')
    if status == HTTPStatus.OK:
        return
    logger.error(f'Error: {response.text}')
    description = HTTPStatus(status).description
    try:
        error_message = json2obj(response.text)
        error_object = ErrorMessage(error_message.transactionId, error_message.errors)
        raise requests.HTTPError(f'HTTP Status: {status}, {description}\n{str(error_object)}', response=error_object)
    except AttributeError:
        logger.error(response)
        raise requests.HTTPError(f'HTTP Status: {status}, {description}', response=response)


def get_stream(url: str, offset: int, confirmation_status: ConfirmationStatus, message_types: [MessageType], security_service: SecurityService):
    params = {
        'offset': offset,
        'messageTypes': message_types and ','.join([message_type.value for message_type in message_types]),
        'confirmationStatus': confirmation_status and confirmation_status.value
    }
    logger.debug(f'Request parameters: {params}')
    headers = security_service.generate_headers(url)
    cookie = security_service.generate_jwt()
    return requests.get(url, stream=True, headers=headers, cookies=cookie, params=params)
