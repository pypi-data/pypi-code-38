

import json

import requests
import urllib3.connectionpool as pool
from urllib3.exceptions import ConnectTimeoutError

from services.delegation.responsehandler import ResponseHandler
from services.exception.exceptions import status_error_handle, ResourceFieldNotFoundException, ConnectionException


def fields(fields):
    class ResourceWrapper(object):
        def __init__(self, *args):
            target = args[0]
            self.wrapped = target
            self.fields = fields

        def __call__(self, *args, **kwargs):
            resource = self.wrapped(*args, **kwargs)
            resource.set_fields(self.fields)
            return resource

    return ResourceWrapper


# def authentication_handler():
#     """Resource must define Authentication handler"""
#     raise StandardError('Abstract Resource must declare')  # pragma: no cover


class Configuration(object):
    def __init__(self, host, auth_handler, handler=None, service_name=None):
        """
        :type host: str
        :param host: Host address
        :type handler: services.delegation.resources.ResponseHandler
        :param handler: Response Handler
        :param auth_handler:
        :param service_name:
        """
        if handler is None:
            handler = JsonResponseHandler()
        self.service_name = service_name
        self.auth_handler = auth_handler
        self.handler = handler
        self.host = host


class AbstractResource(object):
    """
    Extend Abstract resource to implement an external service client.
    """

    def __init__(self, config):
        """
        Declare a resource by host and handler
        :type config: Configuration
        """
        self._fields = []
        # self._connection_pool = None
        self._params = {}
        self._header = None
        self._host = config.host
        self._service_name = config.service_name
        self._params = {}
        self._response_handler = config.handler
        self._auth_handler = config.auth_handler
        self._init = True

    # @property
    # def _logger(self):
    #     return injection.instance(logging.Logger)

    def set_fields(self, source_fields):
        """
        Declare some fields
        :param source_fields: list
        """
        for field in source_fields:
            self._add_property(field)
            self._fields.append(field)

    def _add_property(self, attribute):
        """
        Add property through declared fields
        :param attribute:
        :return:
        """
        getter = lambda self: self._get_property(attribute)
        setter = lambda self, value: self._set_property(attribute, value)

        setattr(self.__class__, attribute, property(fget=getter, fset=setter))

    def _set_property(self, attribute, value):
        self._params[attribute] = value

    def _get_property(self, attribute):
        return self._params[attribute]  # pragma: no cover

    def __setattr__(self, name, value):
        if hasattr(self, '_fields') and hasattr(self, '_init') and name not in self.fields and not hasattr(self, name):
            raise ResourceFieldNotFoundException(self, name)
        super(AbstractResource, self).__setattr__(name, value)

    @property
    def fields(self):
        return self._fields

    def add(self):
        """
        :return:
        """
        raise NotImplementedError

    def get(self):
        """

        :return:
        """
        raise NotImplementedError

    def get_list(self, get_options):
        """

        :return:
        """
        raise NotImplementedError

    def update(self):
        """

        :return:
        """
        raise NotImplementedError

    def delete(self):
        """

        :return:
        """
        raise NotImplementedError

    # @property
    # def connection_pool(self):
    #     """Connection pool for this resource"""
    #     if not self._connection_pool:
    #         self._create_connection_pool(self._host)
    #     return self._connection_pool

    @property
    def response_handler(self):
        """

        :return: services.delegation.resources.ResponseHandler
        """
        return self._response_handler

    @property
    def params(self):
        return self._params

    @property
    def header(self):
        self._header = {}
        if self._auth_handler is not False:
            self._header = self._auth_handler()

        return self._header

    def _perform(self, method, uri, **kwargs):
        # """Perform Resource request"""
        #
        # result = requests.request(method, url=self._host+uri, **kwargs)
        # return self.response_handler.handle(result)
        """Perform Resource request"""
        # try:
            # self._logger.info("%s: %s %s (%s)" % (self._service_name, method, uri, str(self.params)))
        result = requests.request(method, url=self._host+uri, **kwargs)
            # status_error_handle(result)
            # self._params = {}
        return self.response_handler.handle(result)
        # except Exception as e:
        #     # self._logger.error("%s: %s %s has error(%s)" % (self._service_name, method, uri, e.message,))
        #     self.response_handler.on_error(e, self.params)
        #     if isinstance(e, ConnectTimeoutError):
        #         e = ConnectionException()
        #     raise e



    # def _create_connection_pool(self, host):
    #     """
    #     Override this function to provide proper connection pool
    #     Create Connection pool for this service
    #     :type host: str
    #     :param host: address including port localhost:80
    #     :return:
    #     """
    #     conn = pool.connection_from_url(host, maxsize=10, block=True)
    #     self._connection_pool = conn


class APIResource(AbstractResource):
    """Internal API Resource"""

    def __init__(self, config):
        super(APIResource, self).__init__(config)


    def update(self, uri="/", **kwargs):
        return self._perform("PUT", uri, **kwargs)  # pragma: no cover


    def get(self, uri="/", **kwargs):
        return self._perform("GET", uri=uri, **kwargs)


    def delete(self, uri="/", **kwargs):
        self._perform("DELETE", uri, **kwargs)  # pragma: no cover


    @property
    def header(self):
        header = super(APIResource, self).header
        header['Content-Type'] = 'application/json'
        return header


    def add(self, uri="/", **kwargs):
        self._perform("POST", uri, **kwargs)  # pragma: no cover


    def create(self, uri="/", **kwargs):
        self._perform("POST", uri, **kwargs)  # pragma: no cover


class JsonResponseHandler(ResponseHandler):
    @staticmethod
    def handle(response):
        return response.text

    @staticmethod
    def on_error(self, error):
        pass
