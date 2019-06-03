"""Core Curate App Settings
"""
import os
from django.conf import settings

if not settings.configured:
    settings.configure()

REGISTRY_XSD_FILENAME = getattr(settings, 'REGISTRY_XSD_FILENAME', "")
""" str: Registry xsd filename used for the initialisation.
"""


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'core_curate_registry_app/locale'),
)
