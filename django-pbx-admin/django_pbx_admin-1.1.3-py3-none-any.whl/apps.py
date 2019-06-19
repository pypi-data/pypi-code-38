from django.apps import AppConfig


class AdminConfig(AppConfig):
    name = "pbx_admin"

    def ready(self):
        super().ready()
