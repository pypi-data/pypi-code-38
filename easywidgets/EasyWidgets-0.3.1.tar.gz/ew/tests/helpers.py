from __future__ import absolute_import
from __future__ import unicode_literals
import unittest

from paste.registry import Registry
from ew import widget_context, TemplateEngine
from ew.core import WidgetContext
from ew.resource import ResourceManager

REGISTRY = Registry()
REGISTRY.prepare()

class TestCase(unittest.TestCase):

    def setUp(self):
        TemplateEngine.initialize({})
        mgr = ResourceManager()
        REGISTRY.register(
            widget_context,
            WidgetContext(scheme='http', resource_manager=mgr))
