from django.apps import AppConfig


class CBAuthConfig(AppConfig):
    name = 'cbauth'


def ready(self):
    import cbauth.signals
