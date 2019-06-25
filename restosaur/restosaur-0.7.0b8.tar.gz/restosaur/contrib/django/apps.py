from django.apps import AppConfig


class RestosaurAppConfig(AppConfig):
    name = 'restosaur'
    verbose_name = 'Restosaur'

    def ready(self):
        from .settings import (
                AUTODISCOVER_MODULE, AUTODISCOVER_MODULES, AUTODISCOVER)
        from .utils import autodiscover

        if AUTODISCOVER:
            modules = list(AUTODISCOVER_MODULES)

            if AUTODISCOVER_MODULE:
                modules.append(AUTODISCOVER_MODULE)

            autodiscover(*modules)
