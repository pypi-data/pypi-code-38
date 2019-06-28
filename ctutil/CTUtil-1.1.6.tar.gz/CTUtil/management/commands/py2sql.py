from django.core.management.base import BaseCommand
from django.core.management.commands.sqlmigrate import Command as SqlCommand
from typing import Dict, Optional
from datetime import datetime
import io
import os


def sql_format(sql: str, create_datetime: Optional[datetime]=None):
    if not create_datetime:
        create_datetime: datetime = datetime.now()

    _create_datetime: str = format(create_datetime, '%Y-%m-%d %H:%M')
    info: str = f"""
--
--
-- {_create_datetime}
{sql}
--
--


"""
    return info


class Command(BaseCommand):
    help = 'Write Sql From Django Migrate'

    def add_arguments(self, parser):
        parser.add_argument('--source', dest='source')

    def handle(self, *args, **options):
        source = options.setdefault('source', '.')
        if not source:
            raise ValueError('You must need source')

        for root, _dir, _files in os.walk(source):
            root: str
            if not root.endswith('migrations'):
                continue
            else:
                app_name: str = root.split('/')[-2]
                sql_path: str = os.path.join(root, f'{app_name}.sql')
                with open(sql_path, 'w') as f:
                    for _file in _files:
                        _file: str
                        if _file.startswith('__') or not _file.endswith('.py'):
                            continue
                        else:
                            migrate_name: str = _file.split('.')[0]
                            file_update_timestamp: int = os.stat(os.path.join(
                                root, _file
                            )).st_ctime
                            file_update_datetime: datetime = datetime.fromtimestamp(file_update_timestamp)
                            with io.StringIO() as sio:
                                s = SqlCommand(stdout=sio)
                                argvs = ['-', '-', app_name, migrate_name]
                                s.run_from_argv(argvs)
                                sql: str = sio.getvalue()
                            f.write(sql_format(sql, file_update_datetime))