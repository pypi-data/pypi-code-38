# -*- coding: utf-8 -*-

"""
Adapter to use Python str.format() to render a template
"""

from __future__ import absolute_import, unicode_literals, print_function

from string import Formatter

# handle py2 and py3 strings without relying on six lib since we don't use it for anything else.
try:
    basestring
except NameError:
    # if it's good enough for Kenneth Reitz, it's good enough for me
    # https://github.com/kennethreitz/requests/blob/5c4549493b35f5dbb084d029eaf12b6c7ce22579/requests/compat.py#L66
    basestring = (str, bytes)


class DefaultValueFormatter(Formatter):
    """
    String formatter which replaces keys found in the string but not in the replacement parameters
    with a default value.

    The default value for the default is the empty string `''`
    """
    def __init__(self, default=''):
        Formatter.__init__(self)
        self.default = default

    def get_value(self, key, args, kwds):
        if isinstance(key, basestring):
            try:
                return kwds[key]
            except KeyError:
                return self.default
        Formatter.get_value(key, args, kwds)


class StringFormatAdapter(object):
    """
    Adapter for NoteBlockPreprocessor to render templates using standard python string substitution
    using named arguments.
    """
    def render(self, template='', context=None, *args, **kwargs):
        if context is None:
            context = {}
        formatter = DefaultValueFormatter()
        return formatter.format(template, **context)
