from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
import logging

# python manage.py cron <int:frequency>
# python manage.py cron <int:task_id> --id

class Command(BaseCommand):
    help = 'Runs CRON jobs for given frequency'
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('frequency', nargs = 1, type = int)
        parser.add_argument('--id', action = 'store_true', dest = 'id', help = 'Treat the argument as the ID of the CRON job')

    def handle(self, *args, **options):
        from congo.conf import settings

        model_name = settings.CONGO_CRON_MODEL
        if not model_name:
            raise ImproperlyConfigured("In order to use Cron model, configure settings.CONGO_CRON_MODEL first.")
        model = apps.get_model(*model_name.split('.', 1))

        frequency = options['frequency'][0]
        is_cron_id = options['id']

        if is_cron_id:
            try:
                cron_id = frequency
                cron = model.objects.get(id = cron_id)
            except model.DoesNotExist:
                raise CommandError('Incorrect id argument. No CRON job found with ID %s' % cron_id)

            message = "CRON jobs for ID %s invoked" % cron_id
            logger = logging.getLogger('system.cron')
            logger.debug(message)

            cron.run_job(None)

        else:
            try:
                frequency_dict = dict(model.FREQUENCY_CHOICE)
                frequency_label = frequency_dict[frequency]
            except KeyError:
                message = "CRON jobs for frequency %s" % frequency
                logger = logging.getLogger('system.cron')
                logger.error(message)

                raise CommandError('Incorrect frequency argument. Valid values are: %s' % ', '.join(list(frequency_dict.keys())))

            message = "CRON jobs for frequency %s (%s) invoked" % (frequency, frequency_label)
            logger = logging.getLogger('system.cron')
            logger.debug(message)

            i = j = 0

            for cron in model.objects.filter(frequency = frequency, is_active = True):
                if cron.run_job(None):
                    i += 1
                j += 1
