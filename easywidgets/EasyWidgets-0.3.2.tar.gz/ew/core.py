from __future__ import absolute_import
from __future__ import unicode_literals
import logging

from formencode import Invalid
from paste.registry import StackedObjectProxy

widget_context = StackedObjectProxy(name='widget_context')

log = logging.getLogger(__name__)

class WidgetContext(object):
    '''Proxy for the 'ew.widget_context' value in the
    WSGI environ for the current request
    '''

    def __init__(self, scheme, resource_manager):
        self.widget = None
        self.validation_error = None
        self.render_context = None
        self.scheme = scheme
        self.resource_manager = resource_manager

def validator(func):
    def inner(*a, **kw):
        try:
            return func(*a, **kw)
        except Invalid as inv:
            widget_context.validation_error=inv
            raise
    inner.__name__ = str('validator(%s)' % func.__name__)
    return inner

