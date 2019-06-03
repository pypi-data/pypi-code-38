from django.apps import AppConfig


class PbxAdminConfig(AppConfig):
    name = 'pbx_admin'

    def ready(self):
        super().ready()
