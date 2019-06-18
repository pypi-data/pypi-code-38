from optparse import make_option
from string import split

from django.core.management.base import BaseCommand
from ems_client.service import Service


class Command(BaseCommand):
    help = "EMS client utility"

    option_list = BaseCommand.option_list + (
        make_option('--verbose', dest='verbose', default=0, type='int',
                    help='Verbose mode'),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self._service_api = Service()

    def handle(self, *args, **options):
        if len(args):
            command = args[0]
            params = {}
            for arg in args[1:]:
                key, val = split(arg, "=")
                if ',' in val:
                    val = split(val, ',')
                    val = filter(None, val)
                    val = {"int": val}
                params[key] = val
            print(self._service_api._request(command, params))
