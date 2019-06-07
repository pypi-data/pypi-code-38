from __future__ import absolute_import
from __future__ import unicode_literals
import json

from ew.tests.helpers import TestCase
from ew import widget, errors, Snippet, File


class TestWidget(TestCase):

    def test_json(self):
        w = widget.Widget(
            template=Snippet(engine='json'))
        text = w.display()
        assert text == '{"name": null}', text

    def test_defaults(self):
        class SubWidget(widget.Widget):
            template=Snippet(engine='json')
            defaults=dict(
                widget.Widget.defaults,
                a=5,
                b=6)
        dct = json.loads(SubWidget().display())
        assert dct==dict(
            name=None, a=5, b=6), dct
        dct = json.loads(SubWidget(a=10).display())
        assert dct==dict(
            name=None, a=10, b=6), dct
        dct = json.loads(SubWidget(a=10).display(a=4))
        assert dct==dict(
            name=None, a=4, b=6), dct
