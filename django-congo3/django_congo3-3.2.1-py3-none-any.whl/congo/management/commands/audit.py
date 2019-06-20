from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
import logging

# python manage.py audit <int:frequency>
# python manage.py audit <int:audit_id> --id

class Command(BaseCommand):
    help = 'Runs audit tests for given frequency'
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('frequency', nargs = 1, type = int)
        parser.add_argument('--id', action = 'store_true', dest = 'id', help = 'Treat the argument as the ID of the audit test')

    def handle(self, *args, **options):
        from congo.conf import settings

        model_name = settings.CONGO_AUDIT_MODEL
        if not model_name:
            raise ImproperlyConfigured("In order to use Audit model, configure settings.CONGO_AUDIT_MODEL first.")
        model = apps.get_model(*model_name.split('.', 1))

        frequency = options['frequency'][0]
        is_audit_id = options['id']

        if is_audit_id:
            try:
                audit_id = frequency
                audit = model.objects.get(id = audit_id)
            except model.DoesNotExist:
                raise CommandError('Incorrect id argument. No audit test found with ID %s' % audit_id)

            message = "Audit test for ID %s invoked" % audit_id
            logger = logging.getLogger('system.cron')
            logger.debug(message)

            audit.run_job(None)

        else:
            try:
                frequency_dict = dict(model.FREQUENCY_CHOICE)
                frequency_label = frequency_dict[frequency]
            except KeyError:
                message = "Audit tests for frequency %s" % frequency
                logger = logging.getLogger('system.cron')
                logger.error(message)

                raise CommandError('Incorrect frequency argument. Valid values are: %s' % ', '.join(list(frequency_dict.keys())))

            message = "Audit tests for frequency %s (%s) invoked" % (frequency, frequency_label)
            logger = logging.getLogger('system.audit')
            logger.debug(message)

            i = j = 0

            for audit in model.objects.filter(frequency = frequency, is_active = True):
                if audit.run_test(None):
                    i += 1
                j += 1
