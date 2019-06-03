from django.conf import settings

if not settings.configured:
    settings.configure()

SERVER_URI = getattr(settings, 'SERVER_URI', "http://localhost")

INSTALLED_APPS = (
    'core_main_app',
)

DISPLAY_NIST_HEADERS = getattr(settings, 'DISPLAY_NIST_HEADERS', False)
