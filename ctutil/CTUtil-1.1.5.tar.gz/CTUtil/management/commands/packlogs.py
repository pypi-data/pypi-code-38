from django.core.management.base import BaseCommand
from datetime import datetime
import os


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-f', dest='root', default=os.getcwd())
        parser.add_argument('-l', dest='log_file', default='error.log')
        parser.add_argument('-d', dest='log_path', default='logs')

    def handle(self, *args, **options):
        root: str = options.get('root')
        _logs_path: str = options.get('log_path')
        _log_file: str = options.get('log_file')
        logs_path = os.path.join(root, _logs_path)
        log_file = os.path.join(root, _log_file)
        if not os.path.exists(log_file):
            self.stderr.write(f'{log_file} is not exists')
            return
        now_date = datetime.now().date()
        if not os.path.exists(logs_path):
            os.mkdir(logs_path)
        with open(os.path.join(logs_path, f'{format(now_date, "%Y_%m_%d")}.log'), 'wb') as f:
            with open(log_file, 'rb+') as fl:
                f.write(fl.read())
                fl.truncate(0)