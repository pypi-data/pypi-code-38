# encoding: utf-8
from django.apps.registry import apps
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

# python manage.py update_content_types


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

            for model in app.get_models():
                content_type = ContentType.objects.get_for_model(model)
                print "  %s" % content_type

        # @TODO usuwać ct, dla których nie istnieje model
