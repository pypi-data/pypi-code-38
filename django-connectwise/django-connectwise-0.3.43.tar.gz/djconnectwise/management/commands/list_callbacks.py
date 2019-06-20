from django.core.management.base import BaseCommand, CommandError
from djconnectwise.callbacks import CallbacksHandler
from djconnectwise.api import ConnectWiseAPIError
import json


class Command(BaseCommand):
    help = 'List our existing callbacks on ConnectWise.'

    def handle(self, *args, **options):
        handler = CallbacksHandler()
        try:
            callbacks = handler.get_callbacks()
        except ConnectWiseAPIError as e:
            raise CommandError(e)

        # Write out the entire response in JSON; it's not that hard to read.
        self.stdout.write(json.dumps(callbacks, indent=2))
