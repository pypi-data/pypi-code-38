import unittest
import json

from restosaur import API
from restosaur.contrib.apiroot import ApiRoot
from restosaur.contrib.django.dispatch import resource_dispatcher_factory
from .utils import response_content_as_text


class APIRootTestCase(unittest.TestCase):
    def setUp(self):
        super(APIRootTestCase, self).setUp()

        from django.test import RequestFactory

        self.api = API('foo')
        self.root = self.api.resource('/')
        self.apiroot = ApiRoot(self.root)

        self.rqfactory = RequestFactory()

    def call(self, resource, method, *args, **kw):
        rq = getattr(self.rqfactory, method)(resource.path, *args, **kw)
        return resource_dispatcher_factory(self.api, resource)(rq)


class RootPageTestCase(APIRootTestCase):
    def test_successful_returning_status_code_200(self):
        resp = self.call(self.root, 'get')
        self.assertEqual(resp.status_code, 200)

    def test_not_exposing_unregistered_resource(self):
        new_resource = self.api.resource('bar')

        @new_resource.get()
        def bar_get_view(ctx):
            return ctx.Entity()

        resp = self.call(self.root, 'get')
        data = json.loads(response_content_as_text(resp))

        self.assertFalse('bar' in data)

    def test_successful_exposing_registered_resource(self):
        new_resource = self.api.resource('bar')

        @new_resource.get()
        def bar_get_view(ctx):
            return ctx.Entity()

        self.apiroot.register(new_resource, 'bar')

        resp = self.call(self.root, 'get')
        data = json.loads(response_content_as_text(resp))

        self.assertTrue('bar' in data)

    def test_successful_exposing_registered_resource_with_automatic_name(self):
        new_resource = self.api.resource('bar')

        @new_resource.get()
        def bar_get_view(ctx):
            return ctx.Entity()

        self.apiroot.register(new_resource)

        resp = self.call(self.root, 'get')
        data = json.loads(response_content_as_text(resp))

        self.assertTrue('bar' in data)

    def test_exposing_registered_resource_with_valid_uri(self):
        new_resource = self.api.resource('bar')

        @new_resource.get()
        def bar_get_view(ctx):
            return ctx.Entity()

        self.apiroot.register(new_resource)

        resp = self.call(self.root, 'get')
        data = json.loads(response_content_as_text(resp))

        self.assertEqual(data['bar'], 'http://testserver/foo/bar')

    def test_exposing_registered_resource_with_valid_uri_with_parameter(self):
        new_resource = self.api.resource('bar/:id')

        @new_resource.get()
        def bar_get_view(ctx):
            return ctx.Entity()

        self.apiroot.register(new_resource)

        resp = self.call(self.root, 'get')
        data = json.loads(response_content_as_text(resp))

        self.assertEqual(data['bar'], 'http://testserver/foo/bar/:id')


class ApiRootRootResourceRegistrationTestCase(unittest.TestCase):
    def setUp(self):
        super(ApiRootRootResourceRegistrationTestCase, self).setUp()

        from django.test import RequestFactory

        self.api = API('foo')
        self.root_resource = self.api.resource('/')
        self.rqfactory = RequestFactory()

    def call(self, resource, method, *args, **kw):
        rq = getattr(self.rqfactory, method)(resource.path, *args, **kw)
        return resource_dispatcher_factory(self.api, resource)(rq)

    def test_successful_registration_as_a_GET_method(self):
        ApiRoot(self.root_resource)
        self.assertTrue(self.root_resource.is_callback_registered('GET'))

    def test_successful_registration_proper_apiroot_func(self):
        apiroot = ApiRoot(self.root_resource)
        rootfuncname = apiroot.as_view().__name__
        self.assertEqual(
                self.root_resource.get_callback('GET').__name__,
                rootfuncname)

    def test_exception_at_second_registration_apiroot_to_same_rootresource(self):
        ApiRoot(self.root_resource)
        with self.assertRaises(ValueError):
            ApiRoot(self.root_resource)

    def test_that_apiroot_entries_added_after_registration_are_accessible(self):
        apiroot = ApiRoot(self.root_resource)
        bar = self.api.resource('bar')
        apiroot.register(bar)

        resp = self.call(self.root_resource, 'get')
        data = json.loads(response_content_as_text(resp))

        self.assertTrue('bar' in data)
