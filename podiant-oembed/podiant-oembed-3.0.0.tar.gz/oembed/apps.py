from django.conf import settings as settings
from imp import find_module
from importlib import import_module
from django.apps import AppConfig


class OembedAppConfig(AppConfig):
    name = 'oembed'

    def ready(self):
        for app in settings.INSTALLED_APPS:
            import_module(app)
            name = '%s.oembed' % app

            try:
                import_module(name)
            except ImportError as ex:
                try:
                    find_module(name)
                except ImportError:
                    continue

                raise ex  # pragma: no cover
