# -*- coding: utf-8 -*-
from collective.getfeed.interfaces import ICollectivegetfeedCoreLayer
from collective.getfeed.testing import COLLECTIVEGETFEED_CORE_INTEGRATION_TESTING  # noqa
from glob import glob
from httmock import all_requests
from httmock import HTTMock
from plone import api
from zope.interface import alsoProvides

import os
import unittest


@all_requests
def example1(url, request):
    current_dir = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(current_dir, 'examples', 'feed1.rss')
    with open(filename, 'r') as f:
        return {'status_code': 200, 'reason': 'OK', 'content': f.read()}


@all_requests
def example2(url, request):
    current_dir = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(current_dir, 'examples', 'feed2.rss')
    with open(filename, 'r') as f:
        return {'status_code': 200, 'reason': 'OK', 'content': f.read()}


class BaseViewTestCase(unittest.TestCase):

    layer = COLLECTIVEGETFEED_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, ICollectivegetfeedCoreLayer)

        with api.env.adopt_roles(['Manager']):
            self.feed = api.content.create(
                container=self.portal,
                type='Feed',
                id='feed',
                title='Feed title',
                description='Feed description',
                url='http://my.fake.feed/feed',
            )


class FeedViewTestCase(BaseViewTestCase):

    def setUp(self):
        super(FeedViewTestCase, self).setUp()
        self.view = api.content.get_view(
            name=u'view',
            context=self.feed,
            request=self.request
        )


class GetFeedsTestCase(BaseViewTestCase):

    def setUp(self):
        super(GetFeedsTestCase, self).setUp()
        self.view = api.content.get_view(
            name=u'get-feeds',
            context=self.feed,
            request=self.request
        )

    def test_view_first_example(self):
        self.assertEqual(len(self.feed.objectIds()), 0)
        with HTTMock(example1):
            results = self.view.execute()
        self.assertEqual(len(self.feed.objectIds()), 7)
        self.assertIsNotNone(self.feed.get('sabonetes'))

    def test_view_second_example(self):
        self.assertEqual(len(self.feed.objectIds()), 0)
        with HTTMock(example2):
            results = self.view.execute()
        self.assertEqual(len(self.feed.objectIds()), 10)
        self.assertIsNotNone(self.feed.get('pororoca'))

    def test_delete_unlisted_feed(self):
        api.content.create(
            container=self.feed,
            type='Feed Item',
            id='feed-item',
            title='Feed title',
            description='Feed description',
        )
        self.assertEqual(len(self.feed.objectIds()), 1)
        with HTTMock(example1):
            results = self.view.execute()
        self.assertEqual(len(self.feed.objectIds()), 7)
        self.assertIsNotNone(self.feed.get('sabonetes'))
        self.assertIsNone(self.feed.get('feed-item'))

