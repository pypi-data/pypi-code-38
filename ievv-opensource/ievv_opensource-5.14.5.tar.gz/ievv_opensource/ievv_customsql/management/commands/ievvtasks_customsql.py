# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError

from ievv_opensource.ievv_customsql import customsql_registry


class Command(BaseCommand):
    help = 'Run ievv_customsql.'

    def add_arguments(self, parser):
        parser.add_argument('--app', dest='appname',
                            required=False, default=None,
                            help='Only run for a specified Django app.'
                                 'If this is not specified, we run for all apps.')
        parser.add_argument('-i', '--initialize', dest='initialize',
                            required=False, action='store_true',
                            help='Initialize/setup.')
        parser.add_argument('-r', '--recreate-data', dest='recreate_data',
                            required=False, action='store_true',
                            help='Recreate data.')
        parser.add_argument('--clear', dest='clear',
                            required=False, action='store_true',
                            help='Clear data created by --initialize and --recreate-data.')

    def handle(self, *args, **options):
        verbose = options['verbosity'] >= 1
        appname = options['appname']
        clear = options['clear']
        initialize = options['initialize']
        recreate_data = options['recreate_data']
        if not initialize and not recreate_data and not clear:
            raise CommandError('--clear, -i or -r is required, and you can specify all.')

        registry = customsql_registry.Registry.get_instance()
        if appname:
            customsql_iterator = registry.iter_customsql_in_app(appname=appname)
        else:
            customsql_iterator = iter(registry)

        for customsql in customsql_iterator:
            if clear:
                if verbose:
                    self.stdout.write('Clearing: {}'.format(customsql))
                customsql.clear()
            if initialize:
                if verbose:
                    self.stdout.write('Initializing: {}'.format(customsql))
                customsql.initialize()
            if recreate_data:
                if verbose:
                    self.stdout.write('Recreating data for: {}'.format(customsql))
                customsql.recreate_data()
