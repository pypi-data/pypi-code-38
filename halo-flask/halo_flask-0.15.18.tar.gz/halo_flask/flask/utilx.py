from __future__ import print_function

import json
# python
import logging
import re

from flask import Response

from ..base_util import BaseUtil
from ..settingsx import settingsx
from halo_flask.classes import AbsBaseClass

class status(AbsBaseClass):

    def is_informational(code):
        return 100 <= code <= 199

    def is_success(code):
        return 200 <= code <= 299

    def is_redirect(code):
        return 300 <= code <= 399

    def is_client_error(code):
        return 400 <= code <= 499

    def is_server_error(code):
        return 500 <= code <= 599

    HTTP_100_CONTINUE = 100
    HTTP_101_SWITCHING_PROTOCOLS = 101
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_202_ACCEPTED = 202
    HTTP_203_NON_AUTHORITATIVE_INFORMATION = 203
    HTTP_204_NO_CONTENT = 204
    HTTP_205_RESET_CONTENT = 205
    HTTP_206_PARTIAL_CONTENT = 206
    HTTP_207_MULTI_STATUS = 207
    HTTP_300_MULTIPLE_CHOICES = 300
    HTTP_301_MOVED_PERMANENTLY = 301
    HTTP_302_FOUND = 302
    HTTP_303_SEE_OTHER = 303
    HTTP_304_NOT_MODIFIED = 304
    HTTP_305_USE_PROXY = 305
    HTTP_306_RESERVED = 306
    HTTP_307_TEMPORARY_REDIRECT = 307
    HTTP_308_PERMANENT_REDIRECT = 308
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_402_PAYMENT_REQUIRED = 402
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_406_NOT_ACCEPTABLE = 406
    HTTP_407_PROXY_AUTHENTICATION_REQUIRED = 407
    HTTP_408_REQUEST_TIMEOUT = 408
    HTTP_409_CONFLICT = 409
    HTTP_410_GONE = 410
    HTTP_411_LENGTH_REQUIRED = 411
    HTTP_412_PRECONDITION_FAILED = 412
    HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
    HTTP_414_REQUEST_URI_TOO_LONG = 414
    HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
    HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416
    HTTP_417_EXPECTATION_FAILED = 417
    HTTP_428_PRECONDITION_REQUIRED = 428
    HTTP_429_TOO_MANY_REQUESTS = 429
    HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE = 444
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    HTTP_501_NOT_IMPLEMENTED = 501
    HTTP_502_BAD_GATEWAY = 502
    HTTP_503_SERVICE_UNAVAILABLE = 503
    HTTP_504_GATEWAY_TIMEOUT = 504
    HTTP_505_HTTP_VERSION_NOT_SUPPORTED = 505
    HTTP_508_LOOP_DETECTED = 508
    HTTP_510_NOT_EXTENDED = 510
    HTTP_511_NETWORK_AUTHENTICATION_REQUIRED = 511

settings = settingsx()

logger = logging.getLogger(__name__)


def strx(str1):
    """

    :param str1:
    :return:
    """
    if str1:
        try:
            return str1.encode('utf-8').strip()
        except AttributeError as e:
            return str(str1)
        except Exception as e:
            return str(str1)
    return ''

class Util(BaseUtil):

    @staticmethod
    def get_chrome_browser(request):
        """

        :param request:
        :return:
        """
        CHROME_AGENT_RE = re.compile(r".*(Chrome)", re.IGNORECASE)
        NON_CHROME_AGENT_RE = re.compile(
            r".*(Aviator | ChromePlus | coc_ | Dragon | Edge | Flock | Iron | Kinza | Maxthon | MxNitro | Nichrome | OPR | Perk | Rockmelt | Seznam | Sleipnir | Spark | UBrowser | Vivaldi | WebExplorer | YaBrowser)",
            re.IGNORECASE)

        if CHROME_AGENT_RE.match(request.headers['HTTP_USER_AGENT']):
            if NON_CHROME_AGENT_RE.match(request.headers['HTTP_USER_AGENT']):
                return False
            else:
                return True
        else:
            return False

    @staticmethod
    def mobile(request):
        """Return True if the request comes from a mobile device.
        :param request:
        :return:
        """

        MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

        if MOBILE_AGENT_RE.match(request.headers['HTTP_USER_AGENT']):
            return True
        else:
            return False

    @staticmethod
    def get_lambda_context(request):
        """

        :param request:
        :return:
        """
        # AWS_REGION
        # AWS_LAMBDA_FUNCTION_NAME
        # 'lambda.context'
        # x-amzn-RequestId
        if 'lambda.context' in request.headers:
            return request.headers['lambda.context']
        elif 'context' in request.headers:
            return request.headers['context']
        else:
            return None

    @classmethod
    def get_correlation_id(cls, request):
        """

        :param request:
        :return:
        """
        if "HTTP_X_CORRELATION_ID" in request.headers:
            x_correlation_id = request.headers["HTTP_X_CORRELATION_ID"]
        else:
            x_correlation_id = cls.get_aws_request_id(request)
        return x_correlation_id

    @classmethod
    def get_user_agent(cls, request):
        """

        :param request:
        :return:
        """
        if "HTTP_X_USER_AGENT" in request.headers:
            user_agent = request.headers["HTTP_X_USER_AGENT"]
        else:
            user_agent = cls.get_func_name() + ':' + request.path + ':' + request.method + ':' + settings.INSTANCE_ID
        return user_agent

    @classmethod
    def get_debug_enabled(cls, request):
        """

        :param request:
        :return:
        """
        # check if the specific call is debug enabled
        if "HTTP_DEBUG_LOG_ENABLED" in request.headers:
            dlog = request.headers["HTTP_DEBUG_LOG_ENABLED"]
            if dlog == 'true':
                return 'true'
        # check if system wide enabled - done on edge
        if "HTTP_X_CORRELATION_ID" not in request.headers:
            dlog = cls.get_system_debug_enabled()
            if dlog == 'true':
                return 'true'
        return 'false'

    @staticmethod
    def get_headers(request):
        """

        :param request:
        :return:
        """
        regex_http_ = re.compile(r'^HTTP_.+$')
        regex_content_type = re.compile(r'^CONTENT_TYPE$')
        regex_content_length = re.compile(r'^CONTENT_LENGTH$')
        request_headers = {}
        for header, value in request.headers:
            logger.debug("header=" + str(header))
            if regex_http_.match(header) or regex_content_type.match(header) or regex_content_length.match(header):
                request_headers[header] = value  # request.headers[header]
        return request_headers

    @staticmethod
    def get_return_code_tag(request):
        """

        :param request:
        :return:
        """
        tag = "tag"
        if "x-code-tag-id" in request.headers:
            tag = request.headers["x-code-tag-id"]
        return tag

    @staticmethod
    def get_client_ip(request):  # front - when browser calls us
        """

        :param request:
        :return:
        """
        x_forwarded_for = request.headers.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.headers.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def get_server_client_ip(request):  # not front - when service calls us
        """

        :param request:
        :return:
        """
        return request.headers.get('HTTP_REFERER')



    """"
    Success
    response
    return data
    {
        "data": {
            "id": 1001,
            "name": "Wing"
        }
    }
    Error
    response
    return error
    {
        "error": {
            "code": 404,
            "message": "ID not found",
            "requestId": "123-456"
        }
    }
    """

    @staticmethod
    def json_data_response(data, status_code=200, headers=[]):
        """

        :param data:
        :param status_code:
        :return:
        """
        if status_code >= 300:
            return Response(data, status=status_code, headers=headers)
        return Response(json.dumps({"data": data}), status=status_code, headers=headers)

    @staticmethod
    def get_req_params(request):
        """

        :param request:
        :return:
        """
        qd = {}
        if request.method == 'GET':
            qd = request.args
        elif request.method == 'POST':
            qd = request.args
        return qd
