from django.apps import AppConfig
from django.conf import settings

from health_check.plugins import plugin_dir


class HealthCheckConfig(AppConfig):
    name = 'directory_healthcheck'

    def ready(self):
        for backend_class in settings.DIRECTORY_HEALTHCHECK_BACKENDS:
            plugin_dir.register(backend_class)
