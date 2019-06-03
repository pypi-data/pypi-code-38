from django.conf import settings

if not settings.configured:
    settings.configure()

INSTALLED_APPS = getattr(settings, 'INSTALLED_APPS', [])

# MENU
EXPLORE_MENU_NAME = getattr(settings, 'EXPLORE_MENU_NAME', 'Query by Keyword')