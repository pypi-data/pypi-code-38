# -*- coding: utf-8 -*-
"""
Adapter to use Python string.Template to render a template
"""

from __future__ import absolute_import, unicode_literals, print_function

from string import Template


class TemplateStringAdapter(object):

    def render(self, template='', context=None, *args, **kwargs):
        if context is None:
            context = {}

        t = Template(template)
        return t.substitute(**context)
