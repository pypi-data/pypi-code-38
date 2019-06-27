import warnings

from server import template
from server.templatetags.static import (
    do_static as _do_static, static as _static,
)
from server.utils.deprecation import RemovedInServer30Warning

register = template.Library()


def static(path):
    warnings.warn(
        'server.contrib.staticfiles.templatetags.static() is deprecated in '
        'favor of server.templatetags.static.static().',
        RemovedInServer30Warning,
        stacklevel=2,
    )
    return _static(path)


@register.tag('static')
def do_static(parser, token):
    warnings.warn(
        '{% load staticfiles %} is deprecated in favor of {% load static %}.',
        RemovedInServer30Warning,
    )
    return _do_static(parser, token)
