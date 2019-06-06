# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

""" Template tag for printing settings.py into your templates.

{% load settings_value %}

{% settings_value "LANGUAGE_CODE" %} will print LANGUAGE_CODE value
from your settings.py file
"""

from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")