import json
import logging
import os
import re


if os.getenv('DJANGO_SETTINGS_MODULE'):
    from django.conf import settings
else:
    class SettingsObject(object):
        def __init__(self):
            for key in (
                'OEMBED_WIDTH',
                'OEMBED_SANDBOX',
                'OEMBED_URLPATTERNS',
                'OEMBED_CACHE_PREFIX',
                'OEMBED_CACHE_TIMEOUT',
                'OEMBED_AJAX_OBJECT_URL'
            ):
                if os.getenv(key):
                    setattr(self, key, os.getenv(key))

    settings = SettingsObject()


def load_providers():
    filename = os.path.join(
        os.path.dirname(__file__),
        'fixtures',
        'providers.json'
    )

    return json.load(open(filename, 'rb'))


WIDTH = getattr(settings, 'OEMBED_WIDTH', 640)
SANDBOX = getattr(settings, 'OEMBED_SANDBOX', False)
URL_PATTERNS = list(
    getattr(settings, 'OEMBED_URLPATTERNS', [])
) + load_providers()

CACHE_PREFIX = getattr(settings, 'OEMBED_CACHE_PREFIX', 'oembed_')
CACHE_TIMEOUT = getattr(
    settings,
    'OEMBED_CACHE_TIMEOUT',
    getattr(settings, 'CACHES', {}).get('default', {}).get('TIMEOUT', 300)
)

AJAX_OBJECT_URL = getattr(
    settings,
    'OEMBED_AJAX_OBJECT_URL',
    None
)

P_REGEX = re.compile(
    r'<p>([^<\r\n]+)<\/p>', re.IGNORECASE
)

LINK_REGEX = re.compile(r'\<link[^\>]+\>', re.IGNORECASE)
ATTR_REGEX = re.compile(
    r""" ([a-z]+)=(?:"([^"]+)"|'([^']+)')""",
    re.IGNORECASE
)

LINK_TYPE_REGEX = re.compile(r'^application/(json|xml)\+oembed$')
OEMBED_LOGGER = logging.getLogger('oembed')
KNOWN_DOMAINS = getattr(settings, 'OEMBED_KNOWN_DOMAINS', [])


__all__ = [
    'ATTR_REGEX',
    'CACHE_PREFIX',
    'CACHE_TIMEOUT',
    'LINK_REGEX',
    'LINK_TYPE_REGEX',
    'OEMBED_LOGGER',
    'P_REGEX',
    'SANDBOX',
    'URL_PATTERNS',
    'WIDTH'
]
