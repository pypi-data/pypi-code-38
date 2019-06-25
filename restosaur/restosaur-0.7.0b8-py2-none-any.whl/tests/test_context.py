# coding: utf-8
from __future__ import unicode_literals

import datetime
import six
import unittest

from restosaur import API, responses
from restosaur.contrib.django.dispatch import build_context


class ContextTestCase(unittest.TestCase):
    def setUp(self):
        from django.test import RequestFactory

        super(ContextTestCase, self).setUp()

        def create_context(method, path, resource, api=None, **kwargs):
            api = api or self.api
            request = getattr(self.rqfactory, method)(path)
            return api.make_context(
                    host=request.get_host(), path=request.path,
                    request=request, resource=resource,
                    method=method, **kwargs)

        self.api = API('/')
        self.api2 = API('webapi/')
        self.api3 = API('webapi')
        self.rqfactory = RequestFactory()
        self.factory = create_context
        self.ctx = create_context('get', '', lambda ctx: None, api=self.api)
        self.ctx2 = create_context('get', '', lambda ctx: None, api=self.api2)
        self.ctx3 = create_context('get', '', lambda ctx: None, api=self.api3)

    def test_deserialized_property(self):
        ctx = self.factory('get', '/test/', lambda ctx: None, body='body')
        self.assertEqual(ctx.body, ctx.deserialized)


class TestContextBuilidURI(ContextTestCase):
    def test_using_current_location(self):
        ctx = self.factory('get', '/test/', lambda ctx: None)
        self.assertEqual(ctx.build_absolute_uri(), 'http://testserver/test/')

    def test_using_custom_location(self):
        ctx = self.factory('get', '/foo/', lambda ctx: None)
        self.assertEqual(
                ctx.build_absolute_uri('/bar/'), 'http://testserver/bar/')

    def test_appending_custom_parameter_to_current_location(self):
        ctx = self.factory('get', '/foo/', lambda ctx: None)
        self.assertEqual(
                ctx.build_absolute_uri(parameters={'bar': 'baz'}),
                'http://testserver/foo/?bar=baz')

    def test_appending_custom_parameter_to_custom_location(self):
        ctx = self.factory('get', '/foo/', lambda ctx: None)
        url = ctx.build_absolute_uri('/bar/', parameters={'spam': 'eggs'})
        self.assertEqual(url, 'http://testserver/bar/?spam=eggs')

    def test_overriding_parameter_on_current_location(self):
        ctx = self.factory('get', '/foo/?bar=spam', lambda ctx: None)
        url = ctx.build_absolute_uri(parameters={'bar': 'eggs'})
        self.assertEqual(url, 'http://testserver/foo/?bar=eggs')

    def test_overriding_parameter_on_custom_location(self):
        ctx = self.factory('get', '/foo/?bar=spam', lambda ctx: None)
        url = ctx.build_absolute_uri('/baz/', parameters={'bar': 'eggs'})
        self.assertEqual(url, 'http://testserver/baz/?bar=eggs')

    def test_encoding_parameter(self):
        ctx = self.factory('get', '/foo/', lambda ctx: None)
        url = ctx.build_absolute_uri('/baz/', parameters={
            'bar': six.text_type('zażółć')
        })
        self.assertEqual(
                url, 'http://testserver/baz/?bar=za%C5%BC%C3%B3%C5%82%C4%87')

    def test_generating_absolute_uri_using_request_path(self):
        ctx = self.factory('get', '/', lambda ctx: None)
        self.assertEqual(ctx.build_absolute_uri(), 'http://testserver/')

    def test_generating_absolute_uri_using_slash_as_path(self):
        ctx = self.factory('get', '', lambda ctx: None)
        self.assertEqual(ctx.build_absolute_uri('/'), 'http://testserver/')

    def test_generating_absolute_uri_using_double_slash_as_path(self):
        ctx = self.factory('get', '', lambda ctx: None)
        self.assertEqual(ctx.build_absolute_uri('//'), 'http://testserver/')

    def test_generating_absolute_uri_using_triple_slash_as_path(self):
        ctx = self.factory('get', '', lambda ctx: None)
        self.assertEqual(ctx.build_absolute_uri('///'), 'http://testserver/')

    def test_generating_absolute_uri_using_path_with_one_preceding_slash(self):
        ctx = self.factory('get', '', lambda ctx: None)
        self.assertEqual(
                ctx.build_absolute_uri('/some'), 'http://testserver/some')

    def test_generating_absolute_uri_using_path_with_third_preceding_slashes(self):  # NOQA
        ctx = self.factory('get', '', lambda ctx: None)
        self.assertEqual(
                ctx.build_absolute_uri('///some'), 'http://testserver/some')

    def test_generating_absolute_uri_using_path_ending_with_slash(self):
        ctx = self.factory('get', '', lambda ctx: None)
        self.assertEqual(
                ctx.build_absolute_uri('/some/'), 'http://testserver/some/')

    def test_not_replacing_hostname_when_using_two_prepending_slashes_in_build_absolute_uri(self):  # NOQA
        ctx = self.factory('get', '', lambda ctx: None)
        self.assertEqual(
                ctx.build_absolute_uri('//some/'), 'http://testserver/some/')

    def test_successful_generating_uri_using_shortcut_wrapper_to_resource(self):  # NOQA
        res = self.api.resource('foo/:pk')
        ctx = self.factory('get', '/bar/', lambda ctx: None)
        url = ctx.url_for(res, pk='test')
        self.assertEqual(url, 'http://testserver/foo/test')

    def test_generating_uri_for_prefixed_api_and_slash_as_path(self):
        self.assertEqual(
                self.ctx2.build_absolute_uri('/'),
                'http://testserver/webapi/')

    def test_generating_uri_for_prefixed_api_and_path_wihout_preceding_slash(self):  # NOQA
        self.assertEqual(
                self.ctx2.build_absolute_uri('foo'),
                'http://testserver/webapi/foo')

    def test_generating_uri_for_prefixed_api_and_path_wihout_preceding_slash_but_ending_with_slash(self):  # NOQA
        self.assertEqual(
                self.ctx2.build_absolute_uri('foo/'),
                'http://testserver/webapi/foo/')

    def test_generating_uri_for_prefixed_api_without_slash_and_slash_as_path(self):  # NOQA
        self.assertEqual(
                self.ctx3.build_absolute_uri('/'),
                'http://testserver/webapi/')

    def test_generating_uri_for_prefixed_api_without_slash_and_path_wihout_preceding_slash(self):  # NOQA
        self.assertEqual(
                self.ctx3.build_absolute_uri('foo'),
                'http://testserver/webapi/foo')

    def test_generating_uri_for_prefixed_api_without_slash_and_path_wihout_preceding_slash_but_ending_with_slash(self):  # NOQA
        self.assertEqual(
                self.ctx3.build_absolute_uri('foo/'),
                'http://testserver/webapi/foo/')

    def test_successful_building_uri_with_multivalue_query_arg(self):
        ctx = self.factory('get', '', lambda ctx: None)
        uri = ctx.build_absolute_uri('/some', {'foo': ['bar', 'baz']})
        self.assertEqual(uri, 'http://testserver/some?foo=bar&foo=baz')

    def test_successful_getting_mutlivalue_GET_args(self):
        res = self.api.resource('foo')
        rq = self.rqfactory.get('/foo?bar=baz&bar=qux')
        ctx = build_context(self.api, res, rq)
        self.assertTrue('baz' in ctx.parameters['bar'])
        self.assertTrue('qux' in ctx.parameters['bar'])


class TestContextIfModifiedSince(ContextTestCase):
    def test_succesful_parse_rfc_1123_example_time(self):
        from restosaur.context import parse_http_date
        dt = parse_http_date('foo', {'foo': 'Tue, 15 Nov 1994 08:12:31 GMT'})
        self.assertEqual(dt, datetime.datetime(1994, 11, 15, 8, 12, 31))

    def test_error_parse_rfc_1123(self):
        from restosaur.context import parse_http_date
        dt = parse_http_date('foo', {'foo': 'invalid http date'})
        self.assertIsNone(dt)

    def test_that_date_is_modified(self):
        ctx = self.factory('get', '/foo/', lambda ctx: None, headers={
            'if-modified-since': 'Tue, 15 Nov 1994 08:12:31 GMT',
            })
        modification_date = datetime.datetime(1995, 1, 1, 10, 0, 0)
        self.assertTrue(ctx.is_modified_since(modification_date))

    def test_that_date_is_modified_for_invalid_header(self):
        ctx = self.factory('get', '/foo/', lambda ctx: None, headers={
            'if-modified-since': 'invalid http header',
            })
        modification_date = datetime.datetime(1995, 1, 1, 10, 0, 0)
        self.assertTrue(ctx.is_modified_since(modification_date))

    def test_that_date_is_modified_without_header(self):
        ctx = self.factory('get', '/foo/', lambda ctx: None)
        modification_date = datetime.datetime(1995, 1, 1, 10, 0, 0)
        self.assertTrue(ctx.is_modified_since(modification_date))

    def test_that_date_is_not_modified(self):
        ctx = self.factory('get', '/foo/', lambda ctx: None, headers={
            'if-modified-since': 'Tue, 15 Nov 1994 08:12:31 GMT',
            })
        modification_date = datetime.datetime(1990, 1, 1, 10, 0, 0)
        self.assertFalse(ctx.is_modified_since(modification_date))


class TestContextResponseFactories(ContextTestCase):
    def setUp(self):
        super(TestContextResponseFactories, self).setUp()
        self.ctx = self.factory('get', '/foo/', lambda ctx: None)

    def test_base_response(self):
        obj = self.ctx.Response()
        self.assertTrue(isinstance(obj, responses.Response))

    def test_created_response(self):
        obj = self.ctx.Created()
        self.assertTrue(isinstance(obj, responses.CreatedResponse))

    def test_nocontent_response(self):
        obj = self.ctx.NoContent()
        self.assertTrue(isinstance(obj, responses.NoContentResponse))

    def test_unauthorized_response(self):
        obj = self.ctx.Unauthorized()
        self.assertTrue(isinstance(obj, responses.UnauthorizedResponse))

    def test_forbidden_response(self):
        obj = self.ctx.Forbidden()
        self.assertTrue(isinstance(obj, responses.ForbiddenResponse))

    def test_notfound_response(self):
        obj = self.ctx.NotFound()
        self.assertTrue(isinstance(obj, responses.NotFoundResponse))

    def test_methodnotallowed_response(self):
        obj = self.ctx.MethodNotAllowed()
        self.assertTrue(isinstance(obj, responses.MethodNotAllowedResponse))

    def test_notacceptable_response(self):
        obj = self.ctx.NotAcceptable()
        self.assertTrue(isinstance(obj, responses.NotAcceptableResponse))

    def test_entity_response(self):
        obj = self.ctx.Entity()
        self.assertTrue(isinstance(obj, responses.EntityResponse))

    def test_collection_response(self):
        obj = self.ctx.Collection([])
        self.assertTrue(isinstance(obj, responses.CollectionResponse))

    def test_validationerror_response(self):
        obj = self.ctx.ValidationError({})
        self.assertTrue(isinstance(obj, responses.ValidationErrorResponse))

    def test_notmodified_response(self):
        obj = self.ctx.NotModified()
        self.assertTrue(isinstance(obj, responses.NotModifiedResponse))

    def test_seeother_response(self):
        obj = self.ctx.SeeOther('/')
        self.assertTrue(isinstance(obj, responses.SeeOtherResponse))
