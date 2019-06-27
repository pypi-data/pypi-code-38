import unittest
import json

from restosaur import API
from restosaur.contrib.django.dispatch import resource_dispatcher_factory
from .utils import response_content_as_text


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()

        from django.test import RequestFactory

        self.api = API('foo')
        self.collection = self.api.resource('items')
        self.detail = self.api.resource('items/detail')

        @self.detail.get()
        def detail_ctrl(ctx):
            return ctx.OK({'bar': 'baz'})

        @self.detail.post('application/json')
        def detail_post_json(ctx):
            return ctx.OK(ctx.body)

        @self.detail.post('text/plain')
        def detail_post_textplain(ctx):
            return ctx.OK({'bar': ctx.body})

        @self.detail.post('test/error500')
        def detail_post_error500(ctx):
            raise RuntimeError('a runtime error')

        self.rqfactory = RequestFactory()

    def call(self, resource, method, *args, **kw):
        rq = getattr(self.rqfactory, method)(resource.path, *args, **kw)
        return resource_dispatcher_factory(self.api, resource)(rq)


class ContentNegotiationTestCase(BaseTestCase):
    def test_not_acceptable_plaintext_GET(self):
        resp = self.call(self.detail, 'get', HTTP_ACCEPT='text/plain')
        self.assertEqual(resp.status_code, 406)

    def test_successful_plaintext_GET_for_explicite_representation(self):
        @self.detail.representation(media='text/plain')
        def detail_text_plain(obj, ctx):
            return str(obj)
        resp = self.call(self.detail, 'get', HTTP_ACCEPT='text/plain')
        self.assertEqual(resp.content, b"{'bar': 'baz'}")

    def test_successful_json_GET_using_default_representation(self):
        resp = self.call(self.detail, 'get', HTTP_ACCEPT='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_using_global_representation_of_specified_media_type(self):
        @self.detail.representation(model=dict, media='text/plain')
        def detail_text_plain(obj, ctx):
            return str(obj)

        @self.detail.representation(media='text/html')
        def detail_text_html(obj, ctx):
            return '<h1>%s</h1>' % str(obj)

        resp = self.call(
                self.detail, 'get', HTTP_ACCEPT='text/html;q=0.9,*/*;q=0.8')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/html')


class ErrorsContentNegotiationTestCase(BaseTestCase):
    def test_returning_plaintext_error_message(self):
        resp = self.call(
                self.detail, 'post', content_type='test/error500',
                HTTP_ACCEPT='text/plain')
        self.assertIn(b'RuntimeError: a runtime error', resp.content)

    def test_returning_json_error_message(self):
        resp = self.call(
                self.detail, 'post', content_type='test/error500',
                HTTP_ACCEPT='application/json')
        data = json.loads(response_content_as_text(resp))
        self.assertEqual(data['error'], 'a runtime error')

    def test_returning_json_error_message_for_not_accepted_content_type(self):
        resp = self.call(
                self.detail, 'post', content_type='test/error500',
                HTTP_ACCEPT='foo/bar')
        self.assertEqual(resp['Content-Type'], 'application/json')

    def test_returning_plaintex_error_message_for_not_accepted_text_type(self):
        resp = self.call(
                self.detail, 'post', content_type='test/error500',
                HTTP_ACCEPT='text/unsupported')
        self.assertEqual(resp['Content-Type'], 'text/plain')


class DeprecatedResponseTestCase(BaseTestCase):
    def test_returning_406_when_used_base_Response_class(self):
        @self.collection.get()
        def collection_ctrl(ctx):
            return ctx.Response({'items': [{'bar': 'baz'}]})
        resp = self.call(
                self.collection, 'get', HTTP_ACCEPT='text/unsupported')
        self.assertEqual(resp.status_code, 406)


class DefaultQValuesBaseTestCase(BaseTestCase):
    default_qvalues = {}

    def setUp(self):
        super(DefaultQValuesBaseTestCase, self).setUp()

        for key, value in self.default_qvalues.items():
            self.api.set_default_qvalue(key, value)

        @self.detail.representation(
                model=dict, media='application/json')
        def detail_default_app_json(obj, ctx):
            return json.dumps(obj)

        @self.detail.representation(
                model=dict, media='application/vnd.v3+json')
        def detail_default_v3_json(obj, ctx):
            return json.dumps({'data': obj})


class DefaultQValuesOlderPreferredTestCase(DefaultQValuesBaseTestCase):
    default_qvalues = {
            'application/json': 1,
            'application/vnd.v3+json': 0.9,
            }

    def test_that_older_representation_is_returned_as_default(self):
        resp = self.call(self.detail, 'get', HTTP_ACCEPT='*/*')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/json')


class DefaultQValuesNewerPreferredTestCase(DefaultQValuesBaseTestCase):
    default_qvalues = {
            'application/json': 0.9,
            'application/vnd.v3+json': 1,
            }

    def test_that_newer_representation_is_returned_as_default(self):
        resp = self.call(self.detail, 'get', HTTP_ACCEPT='*/*')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/vnd.v3+json')
