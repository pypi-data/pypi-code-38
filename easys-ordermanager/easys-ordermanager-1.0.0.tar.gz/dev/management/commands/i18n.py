import subprocess
from io import StringIO

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'makes and compiles message files'

    FAIL_MESSAGES = [
        'warning: \'msgid\' format string with unnamed arguments cannot be properly localized',
        'warning: Empty msgid.  It is reserved by GNU gettext',
    ]

    def add_arguments(self, parser):
        parser.add_argument('--fail', action='store_true')

    def handle(self, *args, **options):
        self.stdout.write('Making messages')
        out = StringIO()
        call_command('makemessages', locale=['de'], no_location=True, no_obsolete=True, ignore=['docs/*'],
                     extension=['html', 'py', 'txt', 'js', 'tex'], stdout=out)

        self.stdout.write(out.getvalue())

        if options['fail'] and any(x in out.getvalue() for x in self.FAIL_MESSAGES):
            self.stderr.write('Some fail messages were encountered')
            exit(1)

        subprocess.call(["find", ".", "-type", "f", "-name", '*.po', "-exec",
                         "sed", "-i", "-n", "/POT-Creation-Date/!p", "{}", ";"])
        self.stdout.write('Compiling messages')
        call_command('compilemessages', locale=['de'])
