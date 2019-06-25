import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run elasticsearch development server. Required an elasticsearch config ' \
           'in not_for_deploy/elasticsearch.develop.yml.'

    def handle(self, *args, **options):
        os.system('elasticsearch --config=not_for_deploy/elasticsearch.unittest.yml')
