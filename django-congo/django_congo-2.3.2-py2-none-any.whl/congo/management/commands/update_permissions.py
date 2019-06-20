# -*- coding: utf-8 -*-
from django.apps.registry import apps
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

# python manage.py update_permissions


class Command(BaseCommand):
    help = 'Reloads content types for specified apps, or all apps if no args are specified'

    def add_arguments(self, parser):
        parser.add_argument('app_list', nargs = '*', type = str)

    def handle(self, *args, **options):
        app_name_list = options['app_list']
        app_list = []

        if not app_name_list:
            app_list = apps.get_app_configs()
        else:
            for app_name in app_name_list:
                app_list.append(apps.get_app_config(app_name))

        for app in app_list:
            print app.label
            create_permissions(app, app.get_models(), options.get('verbosity', 0))

            for model in app.get_models():
                content_type = ContentType.objects.get_for_model(model)
                codename = "view_%s" % content_type.model

                if not Permission.objects.filter(content_type = content_type, codename = codename).exists():
                    permission = Permission.objects.create(content_type = content_type, codename = codename, name = "Can view %s" % content_type.name)
                    print("Adding permission '%s'" % permission)
