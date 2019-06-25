from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "data_manager_app"
    verbose_name = "data_manager_app"
