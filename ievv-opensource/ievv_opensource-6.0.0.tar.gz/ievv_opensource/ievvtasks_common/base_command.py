from django.core import management
from django.core.management import BaseCommand


class BaseIevvTasksCommand(BaseCommand):
    def run_management_commands(self, management_commands):
        for management_command in management_commands:
            if isinstance(management_command, dict):
                args = management_command.get('args', [])
                options = management_command.get('options', {})
                management_command = management_command['name']
            else:
                args = []
                options = {}
            self.stdout.write(
                'Running management command: {} with '
                'args={!r} and options={!r}.'.format(
                    management_command, args, options))
            management.call_command(management_command, *args, **options)
