from django.conf import settings as site_settings


DEFAULT_RPP = getattr(
    site_settings,
    'API_DEFAULT_RPP',
    100
)

URL_OVERRIDES = getattr(
    site_settings,
    'API_URL_OVERRIDES',
    {
        'auth.user': ('username', lambda o: o.username)
    }
)

DEBUG = getattr(
    site_settings,
    'API_DEBUG',
    getattr(site_settings, 'DEBUG', False)
)

URL_NAMESPACE = getattr(site_settings, 'API_URL_NAMESPACE', 'api')
