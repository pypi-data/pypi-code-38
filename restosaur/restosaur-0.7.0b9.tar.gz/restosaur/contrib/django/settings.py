from django.conf import settings

AUTODISCOVER = getattr(settings, 'RESTOSAUR_AUTODISCOVER', True)
AUTODISCOVER_MODULE = getattr(
        settings, 'RESTOSAUR_AUTODISCOVER_MODULE', 'restapi')
AUTODISCOVER_MODULES = getattr(
        settings, 'RESTOSAUR_AUTODISCOVER_MODULES', [])
