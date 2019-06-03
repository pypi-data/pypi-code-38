"""Core Curate App Settings
"""
import os
from django.conf import settings

if not settings.configured:
    settings.configure()

INSTALLED_APPS = getattr(settings, 'INSTALLED_APPS', [])

PARSER_MIN_TREE = getattr(settings, 'PARSER_MIN_TREE', True)
PARSER_IGNORE_MODULES = getattr(settings, 'PARSER_IGNORE_MODULES', False)
PARSER_COLLAPSE = getattr(settings, 'PARSER_COLLAPSE', True)
PARSER_AUTO_KEY_KEYREF = getattr(settings, 'PARSER_AUTO_KEY_KEYREF', False)
PARSER_IMPLICIT_EXTENSION_BASE = getattr(settings, 'PARSER_IMPLICIT_EXTENSION_BASE', False)
PARSER_DOWNLOAD_DEPENDENCIES = getattr(settings, 'PARSER_DOWNLOAD_DEPENDENCIES', False)

# MENU
CURATE_MENU_NAME = getattr(settings, 'CURATE_MENU_NAME', 'Curator')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'core_curate_app/locale'),
)
