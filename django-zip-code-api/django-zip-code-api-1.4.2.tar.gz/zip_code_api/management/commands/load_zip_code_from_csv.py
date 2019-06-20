# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from zip_code_api.models import Address

# python manage.py load_zip_code_from_csv

class Command(BaseCommand):
    help = 'Load zip code data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type = str)
        parser.add_argument('--i', dest = 'ignore_rows', default = 1, help = 'How many rows to ignore?')
        parser.add_argument('--d', action = 'store_true', dest = 'delete', default = False, help = 'Delete existing addresses')
        parser.add_argument('--e', dest = 'encoding', default = 'Windows-1250', help = 'File encoding')

    def handle(self, *args, **options):
        filename = options['filename']
        ignore_rows = options['ignore_rows']
        delete = options['delete']
        encoding = options['encoding']

        Address.loadFromFile(filename, ignore_rows, delete, encoding)
