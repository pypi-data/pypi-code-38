""" Settings
"""
from django.conf import settings

if not settings.configured:
    settings.configure()

INSTALLED_APPS = getattr(settings, 'INSTALLED_APPS', [])
INSTALLED_APPS.append('oauth2_provider')
