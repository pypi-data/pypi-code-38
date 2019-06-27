from django.conf import settings

settings.configure(**{
    'ALLOWED_HOSTS': ['testserver'],
    'INSTALLED_APPS': ['restosaur'],
    'DEBUG': False,
    })

