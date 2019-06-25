from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "dashboard_app"
    verbose_name = "dashboard_app"
