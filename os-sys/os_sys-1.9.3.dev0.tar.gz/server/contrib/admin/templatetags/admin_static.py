import warnings

from server.template import Library
from server.templatetags.static import static as _static
from server.utils.deprecation import RemovedInServer30Warning

register = Library()


@register.simple_tag
def static(path):
    warnings.warn(
        '{% load admin_static %} is deprecated in favor of {% load static %}.',
        RemovedInServer30Warning,
    )
    return _static(path)
