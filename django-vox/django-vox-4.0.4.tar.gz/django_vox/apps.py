from django.apps import AppConfig


class VoxConfig(AppConfig):
    name = "django_vox"
    verbose_name = "Vox Notifications"

    def ready(self):
        pass
