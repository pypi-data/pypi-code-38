from django.core.management.base import BaseCommand, CommandError
from djangoldp.factories import UserFactory

class Command(BaseCommand):
    help = 'Mock data'

    def add_arguments(self, parser):
        parser.add_argument('--size', type=int, default=0, help='Number of user to create')

    def handle(self, *args, **options):
        UserFactory.create_batch(size=options['size']);

        self.stdout.write(self.style.SUCCESS('Successful data mock install'))
