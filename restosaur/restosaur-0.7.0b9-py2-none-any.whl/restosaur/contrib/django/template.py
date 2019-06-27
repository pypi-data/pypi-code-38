from __future__ import absolute_import

import six

from django.template.loader import render_to_string


@six.python_2_unicode_compatible
class HTMLTemplate(object):
    def __init__(self, context, template_name, template_context):
        self.context = context
        self.template_name = template_name
        self.template_context = template_context
        self._content = None

    def __str__(self):
        if self._content is None:
            self._content = render_to_string(
                request=self.context.request, template_name=self.template_name,
                context=self.template_context)
        return self._content


def render_html(request_context, template_name, context=None):
    return HTMLTemplate(
            request_context, template_name=template_name,
            template_context=context)
