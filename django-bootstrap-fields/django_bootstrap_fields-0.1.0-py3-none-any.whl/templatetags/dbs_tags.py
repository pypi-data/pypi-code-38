from django import forms, template
from django.conf import settings

from .. import utils

register = template.Library()


@register.simple_tag()
def dbs_field(field, inline=False, sr_label=False, prepend=None, append=None):
    """
    Basic usage:
        {% dbs_field field %}
    Advanced usage:
        {% dbs_field field inline=True sr_label=True prepend="$" append=".00" %}
    """
    if not isinstance(field, forms.BoundField) and settings.DEBUG:
        raise Exception('dbs_field: invalid or non-existent field')

    templates = getattr(settings, 'DBS_TEMPLATES', 'bootstrap4')

    dbs_field = utils.render_dbs_field(templates, field, inline, sr_label, prepend, append)
    return dbs_field
