from django.core.management.base import BaseCommand
from django.conf import settings

from populate.populator.common.file_manager import FileManager
from populate.populator.common.populator_actions import PopulatorActions


class Command(BaseCommand):
    help = (
        'Populate service-exo-opportunities'
    )

    def handle(self, *args, **options):
        self.stdout.write('\n Populating {}: \n\n'.format(settings.SERVICE_NAME))

        fm = FileManager(self.stdout, self.stderr)
        fm.prepare_regression_files()
        actions = PopulatorActions(self.stdout, self.stderr)
        actions.populate(settings.POPULATE_ALLOWED_POPULATE_ENTITIES)
        fm.clear_files()
        actions.finish_flag()

        self.stdout.write('\n Populated {}: \n\n'.format(settings.SERVICE_NAME))
