from django.conf import settings
from django.core.management.base import BaseCommand
from ievv_opensource.utils import ievvbuildstatic


class Command(BaseCommand):
    help = 'Show list of NPM package versions that is actually installed.'

    def add_arguments(self, parser):
        parser.add_argument('-a', '--appname', dest='appname',
                            required=False,
                            help='Optional app name.')

    def __make_npminstall_packages(self, app):
        npm = ievvbuildstatic.installers.npm.NpmInstaller(app=app)
        output = [
            'ievvbuildstatic.npminstall.Plugin(',
            '    packages={'
        ]
        for package_name in npm.get_installed_package_names():
            output.append('        {package_name!r}: {version!r},'.format(
                package_name=package_name,
                version=npm.get_package_version(package_name=package_name)
            ))
        output.extend([
            '    }',
            ')'
        ])
        return '\n'.join(output)

    def handle(self, *args, **options):
        appname = options['appname']
        if appname:
            apps = [settings.IEVVTASKS_BUILDSTATIC_APPS.get_app(appname=appname)]
        else:
            apps = settings.IEVVTASKS_BUILDSTATIC_APPS.iterapps()
        for app in apps:
            self.stdout.write('')
            self.stdout.write('*' * 70)
            self.stdout.write('APP: {}'.format(app.appname))
            self.stdout.write('*' * 70)
            self.stdout.write(self.__make_npminstall_packages(app=app))
