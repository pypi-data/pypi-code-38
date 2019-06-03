from __future__ import absolute_import
from __future__ import unicode_literals
import string
from copy import deepcopy

from .core import widget_context
from .utils import push_context, NameListItem, NoDefault
import six

class ExprTemplate(string.Template):
    idpattern = r'[_a-z][^}]*'

class Widget(NameListItem):
    _id = 0
    defaults = dict(
        name=None)
    template=None
    content_type='text/html'

    def __init__(self, **kw):
        super(Widget, self).__init__()
        kw = dict(kw)
        for k,v in six.iteritems(self.defaults):
            if not hasattr(self, k):
                kw.setdefault(k, deepcopy(v))
        for k,v in six.iteritems(kw):
            setattr(self, k, v)

    @classmethod
    def get_params(cls):
        return list(cls.defaults.keys())

    def prepare_context(self, context):
        response = dict(
            (k, getattr(self, k))
            for k in self.get_params())
        response.update(context)
        return response

    def display(self, **kw):
        from .render import File
        context = self.prepare_context(kw)
        with push_context(widget_context, widget=self):
            if isinstance(self.template, six.string_types):
                ename, tname = self.template.split(':', 1)
                self.template = File(tname, ename)
            widget_context.resource_manager.register(self)
            return self.template(context)

    def resources(self):
        return []

    def expand(self, template):
        from ew import Snippet
        tpl = Snippet(template, 'core-ew')
        return tpl(widget_context.render_context)
