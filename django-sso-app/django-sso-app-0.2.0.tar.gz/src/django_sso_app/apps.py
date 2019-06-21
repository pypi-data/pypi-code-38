import logging

from django.apps import AppConfig

logger = logging.getLogger("django_sso_app")


class SsoConfig(AppConfig):
    name = 'django_sso_app'
    verbose_name = "Django Single Sign On App"

    def ready(self):
        from . import settings
        from .utils import get_profile_model

        profile_model = get_profile_model()

        for el in settings.DJANGO_SSO_REQUIRED_PROFILE_FIELDS:
            if getattr(profile_model, el, None) is None:
                raise Exception(
                    'App profile {0} is missing {1} field'.format(profile_model,
                                                                  el))

        super(SsoConfig, self).ready()
        logger.info("Django Single Sign On App is ready!")

