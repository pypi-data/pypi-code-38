# -*- coding: utf-8 -*-

'''
Created on 2014-5-14
@author: hshl.ltd
'''

from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()


@register.simple_tag
def virtual(value):
    virtual_url = ''
    if hasattr(settings, 'VIRTUAL_URL'):
        virtual_url = settings.VIRTUAL_URL
    return mark_safe(u'{0}{1}'.format(virtual_url, value))
