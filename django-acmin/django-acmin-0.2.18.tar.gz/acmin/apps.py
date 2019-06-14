import sys

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from acmin.management import init_models


class AcminConfig(AppConfig):
    name = 'acmin'

    def ready(self):
        post_migrate.connect(init_models)
        if "runserver" in sys.argv:
            from acmin import sql, cache
            sql.patch()
            cache.patch()
