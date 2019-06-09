"""
Command: androidrunserver
=========================


"""


from django.core.management.base import BaseCommand, CommandError
import os
import shutil
import platform

from ._tools import update_apk, overwrite_p4a, post_update_apk

class Command(BaseCommand):
    help = 'Run server through WSGI as in Android.'
    can_import_settings = True


    #----------------------------------------------------------------------
    def handle(self, *args, **options):
        """"""
        from django.conf import settings

        update_apk(settings)
        overwrite_p4a(settings)

        NAME = os.path.split(settings.BASE_DIR)[-1]
        build_dir = os.path.join(settings.ANDROID['BUILD']['build'], NAME)
        name = settings.ANDROID['APK']['name']
        version = settings.ANDROID['APK']['version']
        apk_debug = os.path.join(build_dir, '{}-{}-debug.apk'.format(name, version)).replace(' ', '')
        apk_release = os.path.join(build_dir, '{}-{}-release.apk'.format(name, version)).replace(' ', '')
        package = settings.ANDROID['APK']['package']

        #collectstatic
        app_dir = os.path.join(settings.ANDROID['BUILD']['build'], NAME, 'app')
        os.chdir(os.path.join(app_dir, NAME))
        host_python = "python{}.{}".format(*platform.python_version_tuple()[:2])
        os.system('{} manage.py collectstatic --noinput'.format(host_python))

        post_update_apk(settings)

        main_file = os.path.join(settings.ANDROID['BUILD']['build'], os.path.split(settings.BASE_DIR)[-1], 'app', 'main.py')

        if os.path.exists(main_file):
            os.system('{} {}'.format(host_python, main_file ))
        else:
            print("{} not found!".format(main_file))

