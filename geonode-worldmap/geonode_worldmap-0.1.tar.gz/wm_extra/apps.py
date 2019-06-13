from django.apps import AppConfig


class WMExtraConfig(AppConfig):
    name = 'worldmap.wm_extra'
    verbose_name = 'WM Extras'

    def ready(self):
        from worldmap.wm_extra import signals  # noqa
