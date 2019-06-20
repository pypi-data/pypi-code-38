# -*- coding: utf-8 -*-
from congo.conf import settings
from congo.utils.models import get_model
from django.utils.module_loading import import_string

SITE_CACHE = {}

def get_current_site(request = None):
    if settings.CONGO_SITE_MODEL:
        model = get_site_model()
        return model.objects.get_current(request)
    return None

def get_domain(request, site = None):
    if site is None:
        site = get_current_site(request)

    if site:
        return site.domain
    elif request:
        return request.get_host()
    return settings.ALLOWED_HOSTS[0]

def get_protocol(request, default = None):
    from django.conf import settings as dj_settings
    
    if hasattr(request, 'is_secure'):
        return 'https://' if request.is_secure() else 'http://'
    
    if getattr(dj_settings, 'SECURE_SSL_REDIRECT', False):
        return 'https://'

    return default

def get_site_model():
    return get_model('CONGO_SITE_MODEL')

def get_log_model():
    return get_model('CONGO_LOG_MODEL')

def get_cron_model():
    return get_model('CONGO_CRON_MODEL')

def get_audit_model():
    return get_model('CONGO_AUDIT_MODEL')

def get_admin_model():
    return import_string(settings.CONGO_ADMIN_MODEL)
