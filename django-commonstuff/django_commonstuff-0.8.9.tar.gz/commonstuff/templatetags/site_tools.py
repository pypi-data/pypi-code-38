# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

import warnings

from django import template
from django.conf import settings
try:
    from django.contrib.sites.models import Site
    _sites_imported = True
except ImportError:
    _sites_imported = False
    if settings.DEBUG:
        warnings.warn("Can't import django.contrib.sites.", RuntimeWarning)


register = template.Library()


def _no_request_warning():
    if settings.DEBUG:
        warnings.warn("Request object is not in context for this view.", RuntimeWarning)


def _get_host(context):
    return context['request'].get_host()


@register.simple_tag(takes_context=True)
def get_host(context):
    try:
        return _get_host(context)
    except Exception:
        _no_request_warning()
        return ''


def _get_site_obj(context):
    host = _get_host(context)
    if _sites_imported:
        return Site.objects.filter(domain=host)
    else:
        return None


@register.simple_tag(takes_context=True)
def get_site_obj(context):
    try:
        return _get_site_obj(context)
    except KeyError:
        _no_request_warning()
    return None

