from __future__ import print_function

import importlib
import json
# python
import logging
import os
import random
import uuid

from jsonschema import validate
from .classes import AbsBaseClass
from .exceptions import CacheError, ApiTimeOutExpired
from .settingsx import settingsx
from halo_flask.const import LOC,DEV,TST,PRD

settings = settingsx()

"""
[DEBUG]	2018-07-04T14:43:13.413Z	943ecbc5-7f98-11e8-b37a-5f5dcef64369	APIG: 946fe9db-d4bd-42ec-b0b8-33c701d8f2e2 - environ: 
{'DYNAMODB_URL': 'http://dynamodb.us-east-1.amazonaws.com', '_HANDLER': 'trader1service.handler.lambda_handler', 'AWS_LAMBDA_FUNCTION_VERSION': '$LATEST', 
'FUNC_NAME': 'trader1', u'SERVERTYPE': u'AWS Lambda', 'REDIS_URL': 'rediscache://127.0.0.1:6379/1?client_class=django_redis.client.DefaultClient&password=redis-un-githubbed-password', 
'EXTENSION_URL': 'https://chrome.google.com/webstore/detail/upc-almost-real-time-pric/pkegapagjeenhnhkdmnbkdinffimjmop?hl=en', 
'LAMBDA_TASK_ROOT': '/var/task', 'EXTENSION_ID': 'pkegapagjeenhnhkdmnbkdinffimjmop', 'PATH': '/usr/local/bin:/usr/bin/:/bin', 
'SECRET_KEY': 'z-ba%0c2@udmxs^jrnc(6h-2ukp#g2f34ufo2ks%hrl6pr9z92', 'LD_LIBRARY_PATH': '/lib64:/usr/lib64:/var/runtime:/var/runtime/lib:/var/task:/var/task/lib', 
'LANG': 'en_US.UTF-8', 'TZ': 'America/Chicago', 'SERVER_NAME': 'dev.rtpricer.com', 'AWS_REGION': u'us-east-1', 'AWS_XRAY_CONTEXT_MISSING': 'LOG_ERROR', 
u'FRAMEWORK': u'Zappa', 'AWS_SESSION_TOKEN': 'FQoDYXdzEHYaDPOwF1KU/LgH/Okq/SLkAaYdQteWR6Getm+XB3Ngk1Veb1zaSKz9DzFX9aEMxywxypMsw2ZcU2A/haVSOrCHokPkIsi1P7cb2vr7PlIr5digKgVzchyxTHzNOxDYMWP3yJdvFNfIJ/ydAySNLr/7wGI6GiqXFJSzHuXTsPXoYw8dicMxJ1NY6ru5qSiaD0vDSbV/b+4jVTa2OUX1WLr7WKozTZ40cs/K2Lngc8M3wYn4xj/vq+1Zw93+wU4R51T0FILRlUtqKMHdyq+JxpS5x9hWL494kNXZhrLRdTCybdfJ/+SVRJvNPHGenLcm/O6pHtRZnCiHhPPZBQ==', 
'AWS_SECURITY_TOKEN': 'FQoDYXdzEHYaDPOwF1KU/LgH/Okq/SLkAaYdQteWR6Getm+XB3Ngk1Veb1zaSKz9DzFX9aEMxywxypMsw2ZcU2A/haVSOrCHokPkIsi1P7cb2vr7PlIr5digKgVzchyxTHzNOxDYMWP3yJdvFNfIJ/ydAySNLr/7wGI6GiqXFJSzHuXTsPXoYw8dicMxJ1NY6ru5qSiaD0vDSbV/b+4jVTa2OUX1WLr7WKozTZ40cs/K2Lngc8M3wYn4xj/vq+1Zw93+wU4R51T0FILRlUtqKMHdyq+JxpS5x9hWL494kNXZhrLRdTCybdfJ/+SVRJvNPHGenLcm/O6pHtRZnCiHhPPZBQ==', 
'LAMBDA_RUNTIME_DIR': '/var/runtime', 'PYTHONPATH': '/var/runtime', 'EMAIL_BACKEND': 'django_ses.SESBackend', 'CACHE_URL': 'LocMemCache:///mem', 
u'STAGE': 'dev', 'RC_SECRET_KEY': '6LdnDVcUAAAAAHZVqhLkqLPDF1Hv98ZfibjUIyF0', 'SERVER_LOCAL': 'False', 'STATIC_S3': 'https://s3.amazonaws.com/rtpricer-static/', 
'AWS_LAMBDA_FUNCTION_MEMORY_SIZE': '512', 'SITE_NAME': 'rtpricer.com', 'GA_KEY': 'UA-112752698-2', '_AWS_XRAY_DAEMON_PORT': '2000', 
'_AWS_XRAY_DAEMON_ADDRESS': '169.254.79.2', 'AWS_LAMBDA_LOG_GROUP_NAME': '/aws/lambda/trader1-dev', 'RC_SITE_KEY': '6LdnDVcUAAAAAAChI95HebUvozeZNv7C526nTTDK', 
'DB_VER': '53', 'LOADER_URL': 'https://uw8f0cxo9b.execute-api.us-east-1.amazonaws.com', u'PROJECT': 'trader1', 'DEBUG': 'True', 
'AWS_LAMBDA_LOG_STREAM_NAME': '2018/07/04/[$LATEST]dac7fcd2302f475e84e2efcc14016cff', 'AWS_ACCESS_KEY_ID': 'ASIAIU3RDZ73KXAZT3BA', 
'_X_AMZN_TRACE_ID': 'Root=1-5b3cdd01-9c0d16e2050e40b43ac309c4;Parent=589ee38f0e8efebb;Sampled=0', 'EXTENSION_VER': '0.9', 'AWS_DEFAULT_REGION': 'us-east-1', 
'DJANGO_CONFIGURATION': 'dev', 'DATABASE_URL': 'sqlite:////tmp/db.sqlite3', 'DJANGO_SETTINGS_MODULE': 'trader1service.settings', 
'AWS_SECRET_ACCESS_KEY': '+MV8E2v9VSXTcGTmyvSBrq+S6983i7+Ae7E+dWm+', 'AWS_EXECUTION_ENV': 'AWS_Lambda_python2.7', 'AWS_XRAY_DAEMON_ADDRESS': '169.254.79.2:2000', 
'SECRET_JWT_KEY': '1234567890', 'AWS_LAMBDA_FUNCTION_NAME': 'trader1-dev'}

[DEBUG]	2018-07-04T15:45:41.526Z	4e4dbe1e-7fa1-11e8-8cbc-15a56cf14c11 APIG: 00723a49-2ee7-49bc-b8e8-2a791cb3c773 - headers: {u'HTTP_X_AMZN_TRACE_ID': 'Root=1-5b3ceba5-c1603c1fb3c31bff03ecba11', 
u'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest', u'HTTP_CLOUDFRONT_IS_DESKTOP_VIEWER': 'true', u'HTTP_X_FORWARDED_PROTO': 'https', u'wsgi.multithread': False, 
u'HTTP_X_AMZ_CF_ID': 'LowGhW59Iycq_--oS2AFaRuQ8KeFvMR3zsqIB_hKFEtfkqZruxrp8g==', u'HTTP_CLOUDFRONT_VIEWER_COUNTRY': 'IL', u'SCRIPT_NAME': u'/dev', u'wsgi.input': None, 
u'REQUEST_METHOD': u'GET', u'HTTP_HOST': '3oktz7m6j2.execute-api.us-east-1.amazonaws.com', u'PATH_INFO': u'/top/', u'HTTPS': u'on', u'SERVER_PROTOCOL': 'HTTP/1.1', 
u'QUERY_STRING': 'skip=0&search=&limit=5&_=1530719134240', u'HTTP_CLOUDFRONT_IS_TABLET_VIEWER': 'false', u'HTTP_ACCEPT': '*/*', u'HTTP_CLOUDFRONT_FORWARDED_PROTO': 'https', 
u'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36', u'wsgi.version': (1, 0), 
u'HTTP_COOKIE': '__atuvc=28%7C27; _ga=GA1.4.758072209.1516522643; _gid=GA1.4.252116172.1530566741', u'SERVER_NAME': 'zappa', u'REMOTE_ADDR': u'62.219.237.170', 
u'wsgi.run_once': False, u'wsgi.errors': <__main__.CustomFile object at 0x7f4e5ad56450>, u'wsgi.multiprocess': False, u'HTTP_ACCEPT_LANGUAGE': 'en-US,
en;q=0.9,fr;q=0.8,fr-FR;q=0.7,he-IL;q=0.6,he;q=0.5', u'HTTP_CLOUDFRONT_IS_MOBILE_VIEWER': 'false', u'wsgi.url_scheme': u'https', 
u'HTTP_VIA': '2.0 e4a44efc4b3241dc23019df63a1f645c.cloudfront.net (CloudFront)', u'HTTP_X_FORWARDED_PORT': '443', 
u'HTTP_CLOUDFRONT_IS_SMARTTV_VIEWER': 'false', u'SERVER_PORT': u'443', u'HTTP_X_FORWARDED_FOR': '62.219.237.170, 54.182.239.100', 
u'HTTP_REFERER': 'https://3oktz7m6j2.execute-api.us-east-1.amazonaws.com/dev', u'lambda.context': <__main__.LambdaContext object at 0x7f4e589e3ed0>, 
u'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br'}

/aws/lambda/trader1-yor-dev-trader1 2018/10/04/[$LATEST]1d428b2d6b3140e2affb1411079c7e8c in handle_request {'resource': '/{proxy+}', 'path': '/state/0719192620988/', 'httpMethod': 'GET', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'aws_request_id': '69f453f9-9d79-4999-a606-2e5f4a32b5d5', 'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true', 'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-Country': 'US', 'debug-log-enabled': 'false', 'Host': 'igguvb9ry7.execute-api.us-east-1.amazonaws.com', 'User-Agent': 'python-requests/2.18.4', 'Via': '1.1 aacaf57a89a827fd9e2cbb6fe0d21e43.cloudfront.net (CloudFront)', 'X-Amz-Cf-Id': '-tlbYkrrl5oumBW6pTICkCnyFUZLYvnKFISOwbCaoJOn-TPvXOmx1A==', 'X-Amzn-Trace-Id': 'Root=1-5bb6243c-673f08475eeec7c3f1a3f289', 'x-correlation-id': 'ee4e40f3-976c-4563-bb4f-18af4e35c34d', 'X-Forwarded-For': '54.208.1.115, 52.46.14.108', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https', 'x-user-agent': 'webfront-dev1-webfront:/dev1/page/0719192620988/:GET:3728'}, 'multiValueHeaders': {'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate'], 'aws_request_id': ['69f453f9-9d79-4999-a606-2e5f4a32b5d5'], 'CloudFront-Forwarded-Proto': ['https'], 'CloudFront-Is-Desktop-Viewer': ['true'], 'CloudFront-Is-Mobile-Viewer': ['false'], 'CloudFront-Is-SmartTV-Viewer': ['false'], 'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-Country': ['US'], 'debug-log-enabled': ['false'], 'Host': ['igguvb9ry7.execute-api.us-east-1.amazonaws.com'], 'User-Agent': ['python-requests/2.18.4'], 'Via': ['1.1 aacaf57a89a827fd9e2cbb6fe0d21e43.cloudfront.net (CloudFront)'], 'X-Amz-Cf-Id': ['-tlbYkrrl5oumBW6pTICkCnyFUZLYvnKFISOwbCaoJOn-TPvXOmx1A=='], 'X-Amzn-Trace-Id': ['Root=1-5bb6243c-673f08475eeec7c3f1a3f289'], 'x-correlation-id': ['ee4e40f3-976c-4563-bb4f-18af4e35c34d'], 'X-Forwarded-For': ['54.208.1.115, 52.46.14.108'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https'], 'x-user-agent': ['webfront-dev1-webfront:/dev1/page/0719192620988/:GET:3728']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': {'proxy': 'state/0719192620988'}, 'stageVariables': None, 'requestContext': {'resourceId': 'sc9qkt', 'resourcePath': '/{proxy+}', 'httpMethod': 'GET', 'extendedRequestId': 'OPqZfFR_oAMFayA=', 'requestTime': '04/Oct/2018:14:31:24 +0000', 'path': '/yor-dev/state/0719192620988/', 'accountId': '510393669663', 'protocol': 'HTTP/1.1', 'stage': 'yor-dev', 'requestTimeEpoch': 1538663484747, 'requestId': '2be0822b-c7e2-11e8-b565-b98007fc4e52', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '54.208.1.115', 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'python-requests/2.18.4', 'user': None}, 'apiId': 'igguvb9ry7'}, 'body': None, 'isBase64Encoded': False}

"""

logger = logging.getLogger(__name__)


class BaseUtil(AbsBaseClass):

    def __init__(self):
        pass

    event_req_context = None

    @staticmethod
    def check_if_robot():
        return False

    ################################################################################################

    @classmethod
    def get_aws_request_id(cls, request):
        """

        :param request:
        :return:
        """
        context = cls.get_lambda_context(request)
        if context:
            return context.aws_request_id
        return uuid.uuid4().__str__()

    @staticmethod
    def get_func_name():
        """

        :return:
        """
        if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
            return os.environ['AWS_LAMBDA_FUNCTION_NAME']
        else:
            return settings.FUNC_NAME

    @staticmethod
    def get_func_ver():
        """

        :return:
        """
        if 'AWS_LAMBDA_FUNCTION_VERSION' in os.environ:
            return os.environ['AWS_LAMBDA_FUNCTION_VERSION']
        else:
            return "VER"

    @staticmethod
    def get_func_mem():
        """

        :return:
        """
        if 'AWS_LAMBDA_FUNCTION_MEMORY_SIZE' in os.environ:
            return os.environ['AWS_LAMBDA_FUNCTION_MEMORY_SIZE']
        else:
            return "MEM"

    @staticmethod
    def get_func_region():
        """

        :return:
        """
        if 'AWS_REGION' in os.environ:
            return os.environ['AWS_REGION']
        else:
            if 'AWS_DEFAULT_REGION' in os.environ:
                return os.environ['AWS_DEFAULT_REGION']
            return settings.AWS_REGION


    @staticmethod
    def get_stage():
        """

        :return:
        """
        if 'HALO_STAGE' in os.environ:
            return os.environ['HALO_STAGE']
        return LOC

    @staticmethod
    def get_type():
        """

        :return:
        """
        if 'HALO_TYPE' in os.environ:
            return os.environ['HALO_TYPE']
        return LOC

    @staticmethod
    def get_func():
        """

        :return:
        """
        if 'HALO_FUNC_NAME' in os.environ:
            return os.environ['HALO_FUNC_NAME']
        return settings.FUNC_NAME

    @staticmethod
    def get_app():
        """

        :return:
        """
        if 'HALO_APP_NAME' in os.environ:
            return os.environ['HALO_APP_NAME']
        return settings.APP_NAME

    @classmethod
    def get_context(cls):
        """

        :return:
        """
        ret = {"awsRegion": cls.get_func_region(), "functionName": cls.get_func_name(),
               "functionVersion": cls.get_func_ver(), "functionMemorySize": cls.get_func_mem(),
               "stage": cls.get_stage()}
        return ret



    @staticmethod
    def get_debug_param():
        """

        :return:
        """
        # check if env var for sampled debug logs is on and activate for percentage in settings (5%)
        dbg = 'false'
        if settings.SSM_CONFIG is None:
            return dbg
        try:
            DEBUG_LOG = settings.SSM_CONFIG.get_param('DEBUG_LOG')
            dbg = DEBUG_LOG["val"]
            logger.debug("get_debug_param=" + dbg)
        except CacheError as e:
            pass
        return dbg

    @classmethod
    def get_system_debug_enabled(cls):
        """

        :return:
        """
        # check if env var for sampled debug logs is on and activate for percentage in settings (5%)
        if ('DEBUG_LOG' in os.environ and os.environ['DEBUG_LOG'] == 'true') or (cls.get_debug_param() == 'true'):
            rand = random.random()
            if settings.LOG_SAMPLE_RATE > rand:
                return 'true'
        return 'false'

    @classmethod
    def get_req_context(cls, request, api_key=None):
        """

        :param request:
        :param api_key:
        :return:
        """
        x_correlation_id = cls.get_correlation_id(request)
        x_user_agent = cls.get_user_agent(request)
        dlog = cls.get_debug_enabled(request)
        ret = {"x-user-agent": x_user_agent, "aws_request_id": cls.get_aws_request_id(request),
               "x-correlation-id": x_correlation_id, "debug-log-enabled": dlog, "request_path": request.path}
        if api_key:
            ret["x-api-key"] = api_key
        return ret

    @classmethod
    def isDebugEnabled(cls, req_context, request=None):
        """

        :param req_context:
        :param request:
        :return:
        """
        # disable debug logging by default, but allow override via env variables
        # or if enabled via forwarded request context or if debug flag is on
        if req_context["debug-log-enabled"] == 'true' or cls.get_system_debug_enabled() == 'true':
            return True
        return False

    @staticmethod
    def get_auth_context(request, key=None):
        """

        :param request:
        :param key:
        :return:
        """
        return {}

    @classmethod
    def get_correlation_from_event(cls, event):
        """

        :param event:
        :return:
        """
        if cls.event_req_context:
            logger.debug("cached event req_context", extra=cls.event_req_context)
            return cls.event_req_context
        correlate_id = ''
        user_agent = ''
        debug_flag = ''
        # from api gateway
        if "httpMethod" in event and "requestContext" in event:
            if "headers" in event:
                headers = event["headers"]
                # get correlation-id
                if "x-correlation-id" in headers:
                    correlate_id = headers["x-correlation-id"]
                else:
                    if "aws_request_id" in headers:
                        correlate_id = headers["aws_request_id"]
                    else:
                        correlate_id = uuid.uuid4().__str__()
                # get user-agent = get_func_name + ':' + path + ':' + request.method + ':' + host_ip
                if "x-user-agent" in headers:
                    user_agent = headers["x-user-agent"]
                else:
                    if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
                        func_name = os.environ['AWS_LAMBDA_FUNCTION_NAME']
                    else:
                        if "apiId" in event["requestContext"]:
                            func_name = event["requestContext"]["apiId"]
                        else:
                            func_name = headers["Host"]
                    if "path" in event["requestContext"]:
                        path = event["requestContext"]["path"]
                    else:
                        path = "path"
                    if "httpMethod" in event:
                        method = event["httpMethod"]
                    else:
                        if "httpMethod" in event["requestContext"]:
                            method = event["requestContext"]["httpMethod"]
                        else:
                            method = "method"
                    host_ip = "12.34.56.78"
                    user_agent = str(func_name) + ':' + str(path) + ':' + str(method) + ':' + str(host_ip)
                    logger.debug("user_agent:" + user_agent, extra=cls.event_req_context)
        # from other source
        else:
            if "x-correlation-id" in event:
                correlate_id = event["x-correlation-id"]
            if "x-user-agent" in event:
                user_agent = event["x-user-agent"]
            if "debug-log-enabled" in event:
                debug_flag = event["debug-log-enabled"]
        ret = {"x-user-agent": user_agent, "aws_request_id": '',
               "x-correlation-id": correlate_id, "debug-log-enabled": debug_flag}
        if "x-api-key" in event:
            ret["x-api-key"] = event["x-api-key"]
        # @TODO get all data for request contect
        cls.event_req_context = ret
        return cls.event_req_context



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
    def json_error_response(req_context, clazz, e):  # code, msg, requestId):
        """

        :param req_context:
        :param clazz:
        :param e:
        :return:
        """
        module = importlib.import_module(clazz)
        my_class = getattr(module, 'ErrorMessages')
        msgs = my_class()
        error_code, message = msgs.get_code(e)
        if hasattr(e, 'message'):
            e_msg = e.message
        else:
            e_msg = str(e)
        error_detail = ""
        if e_msg is not None and e_msg != 'None' and e_msg != "":
            error_detail = e_msg
        e_payload = {}
        if hasattr(e, 'payload'):
            e_payload = e.payload
        payload = {"error": {"error_code": error_code, "error_message": message, "error_detail": error_detail,"data":e_payload, "trace_id": req_context["x-correlation-id"]}}
        return error_code, json.dumps(payload)

    @classmethod
    def get_timeout(cls, request):
        """

        :param request:
        :return:
        """
        if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
            context = cls.get_lambda_context(request)
            if context:
                return cls.get_timeout_mili(context)
        return settings.SERVICE_CONNECT_TIMEOUT_IN_SC

    @classmethod
    def get_timeout_mili(cls, context):
        """

        :param context:
        :return:
        """
        mili = context.get_remaining_time_in_millis()
        logger.debug("mili=" + str(mili))
        sc = mili / 1000
        timeout = sc - settings.RECOVER_TIMEOUT_IN_SC
        logger.debug("timeout=" + str(timeout))
        if timeout > settings.MINIMUM_SERVICE_TIMEOUT_IN_SC:
            return timeout
        raise ApiTimeOutExpired("left " + str(timeout))

    @staticmethod
    def assert_valid_schema(data, schema):
        """ Checks whether the given saga json matches the schema """

        return validate(data, schema)


    @staticmethod
    def get_env():
        env = BaseUtil.get_stage()
        print("stage:" + str(env))
        type = BaseUtil.get_type()
        print("type:" + str(type))
        app_config_path = BaseUtil.get_func()
        print("func_name:" + str(app_config_path))
        app_name = BaseUtil.get_app()
        print("app_name:"+str(app_name))
        full_config_path = '/' + app_name + '/' + env + '/' + app_config_path
        short_config_path = '/' + app_name + '/' + type + '/service'
        return full_config_path,short_config_path