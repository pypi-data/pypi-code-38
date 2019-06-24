from django.apps import AppConfig


class IssuestrackerConfig(AppConfig):
    name = 'issuestracker'

    def ready(self):
        from issuestracker import signals  # noqa
