from ftw.topics.interfaces import ITopicBrowserLayer
from ftw.topics.testing import TOPICS_FUNCTIONAL_TESTING
from plone.browserlayer.utils import registered_layers
from unittest2 import TestCase


class TestBrowserLayer(TestCase):

    layer = TOPICS_FUNCTIONAL_TESTING

    def test_request_layer_active(self):
        layers = registered_layers()
        self.assertIn(ITopicBrowserLayer, layers)
