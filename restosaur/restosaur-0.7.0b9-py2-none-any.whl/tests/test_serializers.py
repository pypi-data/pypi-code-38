# coding: utf-8
from __future__ import unicode_literals

from restosaur import API
from restosaur.contrib.django.dispatch import resource_dispatcher_factory
from .utils import response_content_as_text

import unittest
import json


class MultiPartFormSerializerTestCase(unittest.TestCase):
    def setUp(self):
        super(MultiPartFormSerializerTestCase, self).setUp()

        from django.test import RequestFactory
        self.rqfactory = RequestFactory()

        self.api = API('foo')
        self.view = self.api.resource('/')

        @self.view.post('multipart/form-data')
        def view_post_json(ctx):
            return ctx.OK(ctx.body)

        @self.view.representation(media='application/json')
        def view_repr(obj, ctx):
            data = dict(obj.items())
            return data

    def call(self, resource, method, *args, **kw):
        rq = getattr(self.rqfactory, method)(resource.path, *args, **kw)
        return resource_dispatcher_factory(self.api, resource)(rq)

    def test_decoding_multipart_form(self):
        resp = self.call(
                self.view, 'post', data={'foo': 'bar'},
                HTTP_ACCEPT='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(response_content_as_text(resp))
        self.assertEqual(data['foo'], 'bar')
