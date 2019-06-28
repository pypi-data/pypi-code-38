# -*- coding: utf-8 -*-

import hashlib
import json
import time
import uuid
import sys
if sys.version < '3':
    reload(sys)
    sys.setdefaultencoding('utf8')

try:
    from urllib2 import urlopen, Request
    from urlparse import urlparse
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen, Request
    from urllib.parse import urlparse, urlencode

from sdk.exception.access_denied_exception import AccessDeniedException
from sdk.exception.business_exception import BusinessException
from sdk.exception.exceed_limit_exception import ExceedLimitException
from sdk.exception.illegal_request_exception import IllegalRequestException
from sdk.exception.invalid_signature_exception import InvalidSignatureException
from sdk.exception.invalid_timestamp_exception import InvalidTimestampException
from sdk.exception.method_not_allowed_exception import MethodNotAllowedException
from sdk.exception.permission_denied_exception import PermissionDeniedException
from sdk.exception.system_exception import SystemException
from sdk.exception.unauthorized_exception import UnauthorizedException
from sdk.exception.validation_failed_exception import ValidationFailedException


class RpcClient:
    def __init__(self, config, token):
        self.token = token
        self.app_key = config.get_app_key()
        self.secret = config.get_secret()
        self.remote_url = config.get_api_server_url()
        self.log = config.get_log()

    def call(self, action, parameters):
        timestamp = int(round(time.time() * 1000))
        request_id = self.generate_request_id()
        eleme_request_id = request_id + '|' + str(timestamp)
        protocol = {
            "nop": "1.0.0",
            "id": eleme_request_id,
            "action": action,
            "token": json.loads(self.token)['access_token'],
            "metas": {
                "app_key": self.app_key,
                "timestamp": timestamp
            },
            "params": parameters
        }

        protocol['signature'] = self.generate_signature(protocol)

        result = self.post(protocol, eleme_request_id)
        return self.parse_result(result)

    def parse_result(self, result):
        response = json.loads(result)
        if response['error'] != None:
            code = response['error']['code']
            message = response['error']['message']
            if code == "SERVER_ERROR":
                raise SystemException(message)
            elif code == "ILLEGAL_REQUEST":
                raise IllegalRequestException(message)
            elif code == "UNAUTHORIZED":
                raise UnauthorizedException(message)
            elif code == "ACCESS_DENIED":
                raise AccessDeniedException(message)
            elif code == "METHOD_NOT_ALLOWED":
                raise MethodNotAllowedException(message)
            elif code == "PERMISSION_DENIED":
                raise PermissionDeniedException(message)
            elif code == "INVALID_SIGNATURE":
                raise InvalidSignatureException(message)
            elif code == "INVALID_TIMESTAMP":
                raise InvalidTimestampException(message)
            elif code == "VALIDATION_FAILED":
                raise ValidationFailedException(message)
            elif code == "EXCEED_LIMIT":
                raise ExceedLimitException(message)
            else:
                raise BusinessException(message)

        return response['result']

    def generate_signature(self, protocol):
        merged = protocol['metas'].copy()
        merged.update(protocol['params'])
        data = []
        for key in merged:
            value = merged[key]
            data.append(key + "=" + json.dumps(value, ensure_ascii=False, separators=(',', ':')))

        sorted_data = sorted(data)
        splice = protocol['action'] + protocol['token'] + "".join(sorted_data) + self.secret
        hash_value = hashlib.md5(splice.encode("UTF-8")).hexdigest()
        return hash_value.upper()

    def generate_request_id(self):
        req_id = str(uuid.uuid4())
        return req_id.upper().replace('-', '')

    def post(self, data, eleme_request_id):
        self.log.info('request eleme api:{}'.format(json.dumps(data).encode('utf-8')))
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Content-Encoding": "gzip, deflate",
            "User-Agent": "eleme-openapi-python-sdk",
            "x-eleme-requestid": eleme_request_id
        }
        try:
            request = Request(self.remote_url, json.dumps(data).encode('utf-8'), headers)
            response = urlopen(request)
            result = response.read()
            self.log.info('eleme api response:{}'.format(result.decode('utf-8')))
            return result.decode('utf-8')
        except Exception as e:
            self.log.error('eleme api response:{}'.format(e.message))
