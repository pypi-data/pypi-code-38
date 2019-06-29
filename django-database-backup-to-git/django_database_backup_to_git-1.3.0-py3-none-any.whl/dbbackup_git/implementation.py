import os
import subprocess

from django.core.management import call_command
from django.conf import settings

from .utils import change_dir



def add_db_backup(silent=False) -> bool:
    BACKUP_FILENAME = settings.DBBACKUP_GIT['DATABASE_BACKUP_FILENAME']

    with change_dir(os.path.dirname(BACKUP_FILENAME)):
        run_command('git', 'pull')
        create_backup(BACKUP_FILENAME, silent)
        if run_command('git', 'status', '--porcelain').stdout.strip():
            run_command('git', 'add', '.')
            run_command('git', 'commit', '-m', 'Update database backup')
            if settings.DBBACKUP_GIT.get('PUSH', True):
                run_command('git', 'push')
            return True
        return False


def run_command(*command: str):
    return subprocess.run(command, check=True, capture_output=True, text=True)


def create_backup(filename, silent):
    verbosity = 0 if silent else 1
    call_command('dumpdata', indent=2, verbosity=verbosity, output=filename)
