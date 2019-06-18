from urllib.parse import urljoin
from glossary.utils import apply_update
from django.core.management.base import BaseCommand
from glossary import GlossaryService
import json


class Command(BaseCommand):
    help = 'Запрос обновлений'

    def handle(self, *args, **options):
        data = GlossaryService.get_json_models()
        apply_update(json.loads(data))
        self.stdout.write("Обновления успешно загружены")