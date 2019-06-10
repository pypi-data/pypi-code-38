import unittest
import requests
from requests import Session
import json
import httpretty
from dli.client.dli_request_factory_factory import DliRequestFactoryFactory
from dli import __version__
from dli.client.exceptions import (
    DatalakeException,
    InsufficientPrivilegesException,
    UnAuthorisedAccessException
)


class DliRequestFactoryFactoryTestCase(unittest.TestCase):

    @httpretty.activate
    def test_response_403_raises_InsufficientPrivilegesException(self):
        response_text = 'Insufficient Privileges'
        httpretty.register_uri(httpretty.GET, 'http://dummy.com/test', status=403, body=response_text)

        dli_request_factory_factory = DliRequestFactoryFactory('http://dummy.com')

        with self.assertRaises(InsufficientPrivilegesException):
            response = Session().send(dli_request_factory_factory.request_factory(method='GET', url='/test').prepare())

    @httpretty.activate
    def test_response_401_raises_UnAuthorisedAccessException(self):
        response_text = 'UnAuthorised Access'
        httpretty.register_uri(httpretty.GET, 'http://dummy.com/test', status=401, body=response_text)

        dli_request_factory_factory = DliRequestFactoryFactory('http://dummy.com')

        with self.assertRaises(UnAuthorisedAccessException):
            response = Session().send(dli_request_factory_factory.request_factory(method='GET', url='/test').prepare())

    @httpretty.activate
    def test_response_500_raises_DatalakeException(self):
        response_text = 'Datalake server error'
        httpretty.register_uri(httpretty.GET, 'http://dummy.com/test', status=500, body=response_text)

        dli_request_factory_factory = DliRequestFactoryFactory('http://dummy.com')

        with self.assertRaises(DatalakeException):
            response = Session().send(dli_request_factory_factory.request_factory(method='GET', url='/test').prepare())

    @httpretty.activate
    def test_sdk_version_is_included_in_header(self):
        httpretty.register_uri(httpretty.GET, 'http://dummy.com/test', status=200, body="response")
        dli_request_factory_factory = DliRequestFactoryFactory('http://dummy.com')

        # issue a request
        Session().send(dli_request_factory_factory.request_factory(method='GET', url='/test').prepare())

        request = httpretty.last_request()
        self.assertTrue("X-Data-Lake-SDK-Version" in request.headers)
        self.assertEqual(request.headers["X-Data-Lake-SDK-Version"], str(__version__))
