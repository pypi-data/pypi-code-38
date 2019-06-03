import os

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.conf import settings

from populate.populator.common.bulk_operations import BulkOperations
from populate.populator.status import PopulateStatus


class PopulatorActions:
    def __init__(self, stdout, stderr):
        self.status = PopulateStatus()
        self.cmd = BaseCommand(stdout=stdout, stderr=stderr)

    def get_status(self):
        return self.status.get_status()

    def populate(self, items):
        results = {}
        for item in items:
            results[item] = BulkOperations(entity=item, cmd=self.cmd).populate()
        self.sql_sequence_reset()
        self.status.set_populated()
        return results

    def init(self):
        self.status.set_initialized()
        # Execute migrations
        call_command('migrate', stdout=self.cmd.stdout, stderr=self.cmd.stderr)

    def finish_flag(self):
        self.cmd.stdout.write('\n\n\n\n\n\n')
        self.cmd.stdout.write(
            self.cmd.style.SUCCESS('Populator succesfully finished!'))

    def sql_sequence_reset(self):
        if settings.POPULATE_REQUIRED_SEQUENCE_RESET_MODELS:
            sql = call_command(
                'sqlsequencereset',
                *settings.POPULATE_REQUIRED_SEQUENCE_RESET_MODELS,
                no_color=True,
                stdout=self.cmd.stdout, stderr=self.cmd.stderr)
            with connection.cursor() as cursor:
                cursor.execute(sql)

    def is_sql(self, file):
        _, extension = os.path.splitext(file)
        return extension == '.sql'
