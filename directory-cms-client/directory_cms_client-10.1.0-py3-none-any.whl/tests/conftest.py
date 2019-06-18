def pytest_configure():
    from django.conf import settings
    settings.configure(
        URLS_EXCLUDED_FROM_SIGNATURE_CHECK=[],
        DIRECTORY_CMS_API_CLIENT_BASE_URL='https://cms.com',
        DIRECTORY_CMS_API_CLIENT_API_KEY='test-api-key',
        DIRECTORY_CMS_API_CLIENT_SENDER_ID='test-sender',
        DIRECTORY_CMS_API_CLIENT_DEFAULT_TIMEOUT=5,
        DIRECTORY_CMS_API_CLIENT_SERVICE_NAME='foo',
        DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS=10,
        CACHES={
            'cms_fallback': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake',
            }
        }
    )
