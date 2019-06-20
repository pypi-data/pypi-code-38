#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Wed 19 Aug 13:43:50 2015

"""Bob database driver entry-point for the Audio AVspoof Attack Database
"""

import sys
from bob.db.base.driver import Interface as BaseInterface


def reverse(args):
    """Returns a list of file database identifiers given the path stems"""

    from .query import Database
    db = Database()

    output = sys.stdout
    if args.selftest:
        from bob.db.base.utils import null
        output = null()

    r = db.reverse(args.path)
    for id in r: output.write('%d\n' % id)

    if not r: return 1

    return 0


def reverse_command(subparsers):
    """Adds the specific options for the reverse command"""

    from argparse import SUPPRESS

    parser = subparsers.add_parser('reverse', help=reverse.__doc__)

    parser.add_argument('path', nargs='+', type=str,
                        help="one or more path stems to look up. If you provide more than one, files which cannot be reversed will be omitted from the output.")
    parser.add_argument('--self-test', dest="selftest", default=False,
                        action='store_true', help=SUPPRESS)

    parser.set_defaults(func=reverse)  # action


def path(args):
    """Returns a list of fully formed paths or stems given some file id"""

    from .query import Database
    db = Database()

    output = sys.stdout
    if args.selftest:
        from bob.db.base.utils import null
        output = null()

    r = db.paths(args.id, prefix=args.directory, suffix=args.extension)
    for path in r: output.write('%s\n' % path)

    if not r: return 1

    return 0


def path_command(subparsers):
    """Adds the specific options for the path command"""

    from argparse import SUPPRESS

    parser = subparsers.add_parser('path', help=path.__doc__)

    parser.add_argument('-d', '--directory', dest="directory", default='',
                        help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
    parser.add_argument('-e', '--extension', dest="extension", default='',
                        help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")
    parser.add_argument('id', nargs='+', type=int,
                        help="one or more file ids to look up. If you provide more than one, files which cannot be found will be omitted from the output. If you provide a single id to lookup, an error message will be printed if the id does not exist in the database. The exit status will be non-zero in such case.")
    parser.add_argument('--self-test', dest="selftest", default=False,
                        action='store_true', help=SUPPRESS)

    parser.set_defaults(func=path)  # action


class Interface(BaseInterface):
    def name(self):
        return 'avspoof'

    def version(self):
        import pkg_resources  # part of setuptools
        return pkg_resources.require('bob.db.%s' % self.name())[0].version

    def files(self):
        from pkg_resources import resource_filename
        raw_files = ('db.sql3',)
        return [resource_filename(__name__, k) for k in raw_files]

    def type(self):
        return 'sqlite'

    def add_commands(self, parser):
        from . import __doc__ as docs

        subparsers = self.setup_parser(parser,
                                       "Audio AVspoof database", docs)

        # get the "create" action from a submodule
        from .create import add_command as create_command
        create_command(subparsers)

        # get the "dumplist" action from a submodule
        from .dumplist import add_command as dumplist_command
        dumplist_command(subparsers)

        # get the "checkfiles" action from a submodule
        from .checkfiles import add_command as checkfiles_command
        checkfiles_command(subparsers)

        # adds the "reverse" command
        reverse_command(subparsers)

        # adds the "path" command
        path_command(subparsers)

