from django.apps import AppConfig


class CertificationConfig(AppConfig):
    name = 'certification'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
