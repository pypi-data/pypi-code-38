# coding=utf-8
from __future__ import unicode_literals

import logging

from django import template
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.template.defaultfilters import linebreaksbr

from ..utils import fieldlabel as ufieldlabel, fieldvalue as ufieldvalue

logger = logging.getLogger(__name__)

register = template.Library()

@register.filter
def formfieldlabel(form, key):
    return form.fields[key].label

@register.filter
def fieldlabel(obj, key):
    return ufieldlabel(obj, key)

@register.filter
def fieldvalue(obj, key):
    return ufieldvalue(obj, key)

def _get_label_value(obj, key, autoescape):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    label = esc(fieldlabel(obj, key))
    value = fieldvalue(obj, key)
    if hasattr(value, 'get_absolute_url') and not hasattr(value, 'lazycrud_nofollow'):
        value = '<a href="{}">{}</a>'.format(value.get_absolute_url(), esc(value))
    else:
        value = linebreaksbr(esc(value))
    return label, value

@register.filter(needs_autoescape=True)
def dl_item(obj, key, autoescape=None):
    try:
        label, value = _get_label_value(obj, key, autoescape)
        result = '<dt>{}</dt><dd>{}</dd>'.format(label, value)
    except:
        logger.exception('Errore nel rendering del campo %s' % key)
        result = '<dt></dt><dd></dd>'
    return mark_safe(result)

@register.filter(needs_autoescape=True)
def list_item(obj, key, autoescape=None):
    label, value = _get_label_value(obj, key, autoescape)
    result = u'<li><strong>{}:</strong> {}</li>'.format(label, value)
    return mark_safe(result)
