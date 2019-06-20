import os


if os.getenv('DJANGO_SETTINGS_MODULE'):
    from django.core.cache import cache
else:
    class CacheObject(dict):
        def set(self, key, value, timeout=None):
            self[key] = value

    cache = CacheObject()


__all__ = ['cache']
