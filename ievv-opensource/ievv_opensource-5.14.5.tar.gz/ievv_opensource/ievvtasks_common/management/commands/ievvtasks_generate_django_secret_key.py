from django.core.management.base import BaseCommand

from ievv_opensource.utils import secret_key


class Command(BaseCommand):
    help = 'Generate a Django SECRET_KEY.'

    def add_arguments(self, parser):
        parser.add_argument('--plain', dest='plain',
                            required=False, action='store_true',
                            default=False,
                            help='Do not include SECRET_KEY= in output.')
        parser.add_argument('--heroku', dest='heroku',
                            required=False, action='store_true',
                            default=False,
                            help='Output with heroku config:set ...')

    def handle(self, *args, **options):
        key = secret_key.generate_django_secret_key()
        if options['plain']:
            pass
        elif options['heroku']:
            key = 'heroku config:set DJANGO_SECRET_KEY="{}" --app myapp'.format(key)
        else:
            key = 'SECRET_KEY="{}"'.format(key)
        self.stdout.write(key)
