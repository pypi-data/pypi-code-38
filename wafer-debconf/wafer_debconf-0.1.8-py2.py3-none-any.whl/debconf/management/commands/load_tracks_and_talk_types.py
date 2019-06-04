from django.conf import settings
from django.core.management.base import BaseCommand

from wafer.talks.models import Track, TalkType

import yaml


class Command(BaseCommand):
    help = 'Load Track and Talk Type definitions from YAML files into the DB'

    def handle(self, *args, **options):
        with open(settings.TRACKS_FILE) as f:
            tracks = yaml.safe_load(f)
        with open(settings.TALK_TYPES_FILE) as f:
            talk_types = yaml.safe_load(f)

        for item in tracks:
            self.__load__(Track, item)

        for item in talk_types:
            self.__load__(TalkType, item)

    def __load__(self, model, data):
        name = data.pop('name')
        model.objects.update_or_create(name=name, defaults=data)
        self.stdout.write('Loaded %s %s\n' % (model.__name__, name))

