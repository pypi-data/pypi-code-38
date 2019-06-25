import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run development servers configured for this project.'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--name', dest='name',
                            required=False,
                            choices=settings.IEVVTASKS_DEVRUN_RUNNABLES.keys(),
                            default='default')
        parser.add_argument('-q', '--disable-desktop-notifications', dest='enable_desktop_notifications',
                            required=False, action='store_false', default=True)

    def handle(self, *args, **options):
        name = options['name']
        if not options['enable_desktop_notifications']:
            os.environ.setdefault('IEVV_OPENSOURCE_ENABLE_DESKTOP_NOTIFICATIONS', 'false')
        settings.IEVVTASKS_DEVRUN_RUNNABLES[name].start()
