import os

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand


def get_dumpdata_filepath():
    return os.path.join(settings.IEVVTASKS_DUMPDATA_DIRECTORY,
                        'default.sql')


class Command(BaseCommand):
    help = 'Dump the development database as SQL.'

    def handle(self, *args, **options):
        outfile = get_dumpdata_filepath()
        if not os.path.exists(settings.IEVVTASKS_DUMPDATA_DIRECTORY):
            os.makedirs(settings.IEVVTASKS_DUMPDATA_DIRECTORY)
        management.call_command('dbdev_createdump', outfile)
        self.stdout.write('Dumped the database into {}.'.format(
            outfile))
