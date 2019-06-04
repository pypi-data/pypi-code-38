# -*- coding:utf-8 -*- 
__author__ = 'aigo'
from django.conf import settings
from django.shortcuts import urlresolvers

def get_url(request):
    if "REQUEST_URI" in request.META:
        return "%s://%s%s" % (request.scheme, request.get_host(), request.META['REQUEST_URI'])
    else:
        return request.build_absolute_uri()

SERVER_DOMAIN=settings.SERVER_DOMAIN
def reverse_absolute_url(view_name,kwargs,domain=SERVER_DOMAIN,scheme="http"):
    return "%s://%s%s" % (scheme,domain,urlresolvers.reverse(view_name,kwargs=kwargs))