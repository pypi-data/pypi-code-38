""" Core module loval id registry settings
"""
from django.conf import settings

if not settings.configured:
    settings.configure()

LOCAL_ID_LENGTH = getattr(settings, 'LOCAL_ID_LENGTH', 20)
""" int: length used to generate the unique local id.
"""
