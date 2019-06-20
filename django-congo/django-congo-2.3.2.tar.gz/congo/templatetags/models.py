# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.template import Library
from warnings import warn

register = Library()

@register.filter
def content_type_id(obj):
    try:
        return ContentType.objects.get_for_model(obj).id
    except AttributeError:
        return ''

@register.filter
def class_name(obj, full_path = True):
    if full_path:
        return "%s.%s" % (obj.__class__.__module__, obj.__class__.__name__)
    else:
        return obj.__class__.__name__

@register.filter
def field_name(model, field):
    try:
        return model._meta.get_field(field).verbose_name
    except (FieldDoesNotExist, AttributeError):
        return field.replace('-', ' ').replace('_', ' ').title()

@register.filter
def label(obj, field):
    warn(u"Use 'field_name' filter instead.", DeprecationWarning)

    return obj._meta.get_field(field).verbose_name

