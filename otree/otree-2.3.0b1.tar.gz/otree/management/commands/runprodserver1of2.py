import os
import re
import sys
import logging

import honcho.manager

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
import otree

logger = logging.getLogger(__name__)

naiveip_re = re.compile(r"""^(?:
(?P<addr>
    (?P<ipv4>\d{1,3}(?:\.\d{1,3}){3}) |         # IPv4 address
    (?P<ipv6>\[[a-fA-F0-9:]+\]) |               # IPv6 address
    (?P<fqdn>[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*) # FQDN
):)?(?P<port>\d+)$""", re.X)

DEFAULT_PORT = "8000"
DEFAULT_ADDR = '0.0.0.0'

# "You'll need to run uvicorn from the command line if you want multi-workers with windows."
# https://github.com/encode/uvicorn/issues/342#issuecomment-480230739
if sys.platform.startswith("win"):
    NUM_UVICORNS = 1
else:
    NUM_UVICORNS = 3

def get_ssl_file_path(filename):
    otree_dir = os.path.dirname(otree.__file__)
    pth = os.path.join(otree_dir, 'certs', filename)
    return pth.replace('\\', '/')

# made this simple class to reduce code duplication,
# and to make testing easier (I didn't know how to check that it was called
# with os.environ.copy(), especially if we patch os.environ)
class OTreeHonchoManager(honcho.manager.Manager):
    def add_otree_process(self, name, cmd):
        self.add_process(name, cmd, env=os.environ.copy(), quiet=False)


class Command(BaseCommand):
    help = 'oTree production server.'

    def add_arguments(self, parser):

        parser.add_argument('addrport', nargs='?',
            help='Optional port number, or ipaddr:port')

        ahelp = (
            'Run an SSL server directly in Daphne with a self-signed cert/key'
        )
        parser.add_argument(
            '--dev-https', action='store_true', dest='dev_https', default=False,
            help=ahelp)

    def handle(self, *args, addrport=None, verbosity=1, dev_https, **kwargs):
        self.verbosity = verbosity
        self.honcho = OTreeHonchoManager()
        self.setup_honcho(addrport=addrport, dev_https=dev_https)
        self.honcho.loop()
        sys.exit(self.honcho.returncode)

    def setup_honcho(self, *, addrport, dev_https):

        if addrport:
            m = re.match(naiveip_re, addrport)
            if m is None:
                raise CommandError('"%s" is not a valid port number '
                                   'or address:port pair.' % addrport)
            addr, _, _, _, port = m.groups()
        else:
            addr = None
            port = None

        addr = addr or DEFAULT_ADDR
        port = port or os.environ.get('PORT') or DEFAULT_PORT

        uvicorn_cmd = f'uvicorn --host={addr} --port={port} --workers={NUM_UVICORNS} otree_startup.asgi:application'

        if dev_https:
            uvicorn_cmd += ' --ssl-keyfile="{}" --ssl-certfile="{}"'.format(
                get_ssl_file_path('development.key'),
                get_ssl_file_path('development.crt'),
            )

        logger.info(uvicorn_cmd)

        honcho = self.honcho
        honcho.add_otree_process(
            'uvicorn',
            uvicorn_cmd
        )
