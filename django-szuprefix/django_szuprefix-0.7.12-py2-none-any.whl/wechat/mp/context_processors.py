"""
A set of request processors that return dictionaries to be merged into a
template context. Each function takes the request object as its only parameter
and returns a dictionary to add to the context.

These are referenced from the setting TEMPLATE_CONTEXT_PROCESSORS and used by
RequestContext.
"""
from __future__ import unicode_literals
from django_szuprefix.utils import httputils
from .helper import api

def wxConfig(request): 
    try:
        return {'wxConfig': api.get_jsapi_params(httputils.get_url(request)) }
    except:
        return {}
