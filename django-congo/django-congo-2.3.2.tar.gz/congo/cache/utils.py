# -*- coding: utf-8 -*-
from congo.conf import settings
from django.utils.translation import get_language

def cache_key_generator(key, key_prefix, version):
    key_elemets = []

    cache_key_prefix = getattr(settings, 'CACHE_KEY_PREFIX', None)
    if cache_key_prefix:
        key_elemets.append(cache_key_prefix)

    if key_prefix:
        key_elemets.append(str(key_prefix))

    key_elemets.append(key)

    if version:
        key_elemets.append(str(version))

    site_id = getattr(settings, 'SITE_ID', None)
    if site_id and settings.CONGO_CACHE_KEY_APPEND_SITE_ID:
        key_elemets.append(str(site_id))

    language = get_language() or getattr(settings, 'LANGUAGE_CODE', None)
    if language and settings.CONGO_CACHE_KEY_APPEND_LANGUAGE:
        key_elemets.append(language)

    return ':'.join(key_elemets)
