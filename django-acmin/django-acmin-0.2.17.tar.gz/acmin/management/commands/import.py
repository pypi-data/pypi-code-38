import time

import django.apps
import requests
from django.core.management.commands import loaddata


# python manage.py import host.com
class Command(loaddata.Command):
    def add_arguments(self, parser):
        super().add_arguments(parser)

    def handle(self, *args, **options):
        from django.conf import settings
        app_name = getattr(settings, "APP_NAME")
        if not settings.DEBUG: return
        for model in django.apps.apps.get_models():
            model.objects.all().delete()
        host = args[0]
        today = time.strftime("%Y-%m-%d")
        name = f"{today}.json.gz"
        url = f"https://{host}/backup/{app_name}/{name}"
        r = requests.get(url, stream=True)
        file = f"/tmp/{app_name}-{name}"
        f = open(file, "wb")
        for chunk in r.iter_content(chunk_size=512):
            if chunk: f.write(chunk)
        f.close()
        super().handle(*(file,), **options)
