from subprocess import CalledProcessError

from django.core.management.base import BaseCommand, CommandError

from dbbackup_git.implementation import add_db_backup
from django.conf import settings

class Command(BaseCommand):
    help = f"Update database backup in JSON format, commit and push it with Git"

    def add_arguments(self, parser):
        parser.add_argument(
            '--silent', action='store_true', dest='silent',
            help="Do not show success message",
        )

    def handle(self, **options):
        assert hasattr(settings, 'DBBACKUP_GIT'), '`dbbackup_git` app requires the `DBBACKUP_GIT` setting.'
        assert settings.DBBACKUP_GIT.get('DATABASE_BACKUP_FILENAME', None), \
            "`dbbackup_git` app requires the `DBBACKUP_GIT['DATABASE_BACKUP_FILENAME']` setting."

        try:
            created = add_db_backup(options['silent'])
            if not options['silent']:
                message = 'Backup was created successfully' if created else 'No changes detected'
                self.stdout.write(self.style.SUCCESS(message))
        except CalledProcessError as e:
            output = f'{e.stdout}\n{e.stderr}'
            self.stderr.write(self.style.ERROR(f'ERROR: {e}\nOUTPUT: {output}'))
