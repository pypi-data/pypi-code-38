from urllib.parse import urljoin

from django.core.management.base import BaseCommand
from django.urls import reverse

from glossary import GlossaryService


class Command(BaseCommand):
    help = 'Регистрация приложения для использования глоссария'

    def add_arguments(self, parser):
        parser.add_argument('host', type=str)

    def handle(self, *args, **options):
        host = options["host"]
        update_url = reverse("glossary-update")
        full_url = urljoin(host, update_url)
        token = GlossaryService.register(full_url)
        self.stdout.write(
            "Добавьте GLOSSARY_SERVICE_TOKEN = '{}' в Django settings"
            .format(token)
        )