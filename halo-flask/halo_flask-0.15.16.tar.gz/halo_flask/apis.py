from __future__ import print_function

# python
import datetime
import importlib
import logging
import time
from abc import ABCMeta

import requests

from .classes import AbsBaseClass
from .exceptions import MaxTryHttpException, ApiError
from .logs import log_json
from .settingsx import settingsx
from halo_flask.const import LOC,DEV,TST,PRD
from .flask.utilx import Util

settings = settingsx()

# DRF



logger = logging.getLogger(__name__)



from halo_flask.circuitbreaker import CircuitBreaker
class MyCircuitBreaker(CircuitBreaker):
    def __init__(self):
        FAILURE_THRESHOLD =  self.get_failure_threshold()
        RECOVERY_TIMEOUT = self.get_recovery_timeout()
        EXPECTED_EXCEPTION = Exception
        super(MyCircuitBreaker, self).__init__(FAILURE_THRESHOLD,RECOVERY_TIMEOUT,EXPECTED_EXCEPTION)

    def get_failure_threshold(self):
        FAILURE_THRESHOLD = 3
        if settings.HTTP_MAX_RETRY:
            FAILURE_THRESHOLD = settings.HTTP_MAX_RETRY
        return FAILURE_THRESHOLD

    def get_recovery_timeout(self):
        RECOVERY_TIMEOUT = 15
        if settings.HTTP_RETRY_SLEEP:
            RECOVERY_TIMEOUT = settings.HTTP_RETRY_SLEEP
        return RECOVERY_TIMEOUT


class AbsBaseApi(AbsBaseClass):
    __metaclass__ = ABCMeta

    name = None
    url = None
    api_type = None
    req_context = None
    cb = MyCircuitBreaker()

    def __init__(self, req_context):
        self.req_context = req_context
        self.url, self.api_type = self.get_url_str()
        self.cb._name = self.name

    @cb
    def do_request(self,method, url, timeout, data=None, headers=None, auth=None):
        return requests.request(method, url, data=data, headers=headers,
                         timeout=timeout, auth=auth)

    def exec_client(self, req_context, method, url, api_type, timeout, data=None, headers=None, auth=None):
        """

        :param req_context:
        :param method:
        :param url:
        :param api_type:
        :param timeout:
        :param data:
        :param headers:
        :return:
        """

        msg = "Max Try for url: ("+str(settings.HTTP_MAX_RETRY)+") " + str(url)
        for i in range(0, settings.HTTP_MAX_RETRY):
            logger.debug("try index: "+str(i), extra=log_json(req_context))
            try:
                logger.debug("try: " + str(i), extra=log_json(req_context))
                ret = self.do_request(method, url, timeout, data=None, headers=None, auth=None)
                logger.debug("status_code=" + str(ret.status_code), extra=log_json(req_context))
                if ret.status_code >= 500:
                    continue
                if 200 > ret.status_code or 500 > ret.status_code >= 300:
                    err = ApiError("error status_code " + str(ret.status_code) + " in : " + url)
                    err.status_code = ret.status_code
                    err.stack = None
                    raise err
                return ret
            except requests.exceptions.ReadTimeout as e:  # this confirms you that the request has reached server
                logger.debug(str(e))
                logger.debug(
                    "ReadTimeout " + str(
                        settings.SERVICE_READ_TIMEOUT_IN_MS) + " in method=" + method + " for url=" + url,
                    extra=log_json(req_context))
                continue
            except requests.exceptions.ConnectTimeout as e:
                logger.debug(str(e))
                logger.debug("ConnectTimeout in method=" + str(
                    settings.SERVICE_CONNECT_TIMEOUT_IN_MS) + " in method=" + method + " for url=" + url,
                             extra=log_json(req_context))
                continue
        raise MaxTryHttpException(msg)

    def get_url_str(self):
        """

        :return:
        """
        api_config = settings.API_CONFIG
        logger.debug("api_config: " + str(api_config), extra=log_json(self.req_context))
        return api_config[self.name]["url"], api_config[self.name]["type"]

    def set_api_url(self, key, val):
        """

        :param key:
        :param val:
        :return:
        """
        strx = self.url
        strx = strx.replace("$" + str(key), str(val))
        logger.debug("url replace var: " + strx, extra=log_json(self.req_context))
        self.url = strx
        return self.url

    def set_api_query(self, query):
        """

        :param query:
        :return:
        """
        strx = self.url
        if "?" in self.url:
            strx = strx + "&" + query
        else:
            strx = strx + "?" + query
        logger.debug("url add query: " + strx, extra=log_json(self.req_context))
        self.url = strx
        return self.url

    def set_api_params(self, params):
        """

        :param params:
        :return:
        """
        strx = self.url
        if "?" in self.url:
            strx = strx + "&" + params
        else:
            strx = strx + "?" + params
        logger.debug("url add query: " + strx, extra=log_json(self.req_context))
        self.url = strx
        return self.url

    def process(self, method, url, timeout, data=None, headers=None,auth=None):
        """

        :param method:
        :param url:
        :param timeout:
        :param data:
        :param headers:
        :return:
        """
        try:
            logger.debug("Api name: "+self.name+" method: " + str(method) + " url: " + str(url), extra=log_json(self.req_context))
            now = datetime.datetime.now()
            ret = self.exec_client(self.req_context, method, url, self.api_type, timeout, data=data, headers=headers,auth=auth)
            total = datetime.datetime.now() - now
            logger.info("performance_data", extra=log_json(self.req_context,
                                                           {"type": "API", "milliseconds": int(total.total_seconds() * 1000),
                                                       "url": str(url)}))
            logger.debug("ret: " + str(ret), extra=log_json(self.req_context))
            return ret
        except requests.ConnectionError as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.req_context))
            er = ApiError(e)
            er.status_code = 500
            raise er
        except requests.HTTPError as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.req_context))
            er = ApiError(e)
            er.status_code = 500
            raise er
        except requests.Timeout as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.req_context))
            er = ApiError(e)
            er.status_code = 500
            raise er
        except requests.RequestException as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.req_context))
            er = ApiError(e)
            er.status_code = 500
            raise er
        except ApiError as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.req_context))
            raise e

    def get(self, timeout, headers=None,auth=None):
        """

        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process('GET', self.url, timeout, headers=headers,auth=auth)

    def post(self, data, timeout, headers=None,auth=None):
        """

        :param data:
        :param timeout:
        :param headers:
        :return:
        """
        logger.debug("payload=" + str(data))
        if headers is None:
            headers = headers
        return self.process('POST', self.url, timeout, data=data, headers=headers,auth=auth)

    def put(self, data, timeout, headers=None,auth=None):
        """

        :param data:
        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process('PUT', self.url, timeout, data=data, headers=headers,auth=auth)

    def patch(self, data, timeout, headers=None,auth=None):
        """

        :param data:
        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process('PATCH', self.url, timeout, data=data, headers=headers,auth=auth)

    def delete(self, timeout, headers=None,auth=None):
        """

        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process('DELETE', self.url, timeout, headers=headers,auth=auth)

    def fwd_process(self, typer, request, vars, headers,auth=None):
        """

        :param typer:
        :param request:
        :param vars:
        :param headers:
        :return:
        """
        verb = typer.value
        if verb == 'GET' or 'DELETE':
            data = None
        else:
            data = request.data
        return self.process(verb, self.url, Util.get_timeout(request), data=data, headers=headers,auth=auth)

API_LIST = {"Google": 'GoogleApi', "Cnn": "ApiTest"}
class ApiMngr(AbsBaseClass):

    def __init__(self, req_context):
        logger.debug("ApiMngr=" + str(req_context))
        self.req_context = req_context

    @staticmethod
    def get_api(name):
        """

        :param name:
        :return:
        """
        logger.debug("get_api=" + name)
        if name in API_LIST:
            return API_LIST[name]
        return None

    def get_api_instance(self, class_name, **kwargs):
        """

        :param class_name:
        :param kwargs:
        :return:
        """
        logger.debug("get_api_insance=" + class_name)
        module = importlib.import_module(__name__)
        class_ = getattr(module, class_name)
        instance = class_(self.req_context)
        logger.debug("class=" + str(instance))
        return instance

SSM_CONFIG = None
SSM_APP_CONFIG = None
def load_api_config(stage_type,ssm_type,func_name,API_CONFIG):
    global SSM_CONFIG
    global SSM_APP_CONFIG

    if stage_type == LOC:
        # from halo_flask.ssm import get_config as get_config
        try:
            from halo_flask.halo_flask.ssm import get_config
        except:
            from halo_flask.ssm import get_config

        SSM_CONFIG = get_config(ssm_type)
        # set_param_config(AWS_REGION, 'DEBUG_LOG', '{"val":"false"}')
        # SSM_CONFIG.get_param("test")

        # from halo_flask.ssm import get_config as get_config
        try:
            from halo_flask.halo_flask.ssm import get_app_config
        except:
            from halo_flask.ssm import get_app_config

        SSM_APP_CONFIG = get_app_config(ssm_type)

        # api_config:{'About': {'url': 'http://127.0.0.1:7000/about/', 'type': 'api'}, 'Task': {'url': 'http://127.0.0.1:7000/task/$upcid/', 'type': 'api'}, 'Curr': {'url': 'http://127.0.0.1:7000/curr/', 'type': 'api'}, 'Top': {'url': 'http://127.0.0.1:7000/top/', 'type': 'api'}, 'Rupc': {'url': 'http://127.0.0.1:7000/upc/$upcid/', 'type': 'api'}, 'Upc': {'url': 'http://127.0.0.1:7000/upc/$upcid/', 'type': 'api'}, 'Contact': {'url': 'http://127.0.0.1:7000/contact/', 'type': 'api'}, 'Fail': {'url': 'http://127.0.0.1:7000/fail/', 'type': 'api'}, 'Rtask': {'url': 'http://127.0.0.1:7000/task/$upcid/', 'type': 'api'}, 'Page': {'url': 'http://127.0.0.1:7000/page/$upcid/', 'type': 'api'}, 'Sim': {'url': 'http://127.0.0.1:7000/sim/', 'type': 'api'}, 'Google': {'url': 'http://www.google.com', 'type': 'service'}}
        for item in SSM_APP_CONFIG.cache.items:
            if item not in [func_name, 'DEFAULT']:
                url = SSM_APP_CONFIG.get_param(item)["url"]
                print(item + ":" + url)
                for key in API_CONFIG:
                    current = API_CONFIG[key]
                    new_url = current["url"]
                    if "service://" + item in new_url:
                        API_CONFIG[key]["url"] = new_url.replace("service://" + item, url)
        print(str(API_CONFIG))

##################################### test #########################
from halo_flask.apis import AbsBaseApi

class ApiTest(AbsBaseApi):
    name = 'Cnn'


class GoogleApi(AbsBaseApi):
    name = 'Google'
