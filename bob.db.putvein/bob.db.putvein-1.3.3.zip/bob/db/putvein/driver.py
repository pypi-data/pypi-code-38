#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Bob Database Driver entry-point for the PUT Vein Database.
"""

import os
import sys
from bob.db.base.driver import Interface as BaseInterface
from .query import Database


# Driver API
# ==========

def dumplist(args):
    """Dumps lists of files based on your criteria"""

    db = Database()

    objects = db.objects(
        protocol=args.protocol,
        purposes=args.purposes,
        groups=args.groups,
        kinds=args.kinds
    )

    output = sys.stdout
    if args.selftest:
        from bob.db.base.utils import null
        output = null()

    for obj in objects:
        output.write('%s\n' % obj.make_path(directory=args.directory))

    return 0


def checkfiles(args):
    """Checks the existence of the files based on your criteria"""

    db = Database()

    objects = db.objects(
        protocol=args.protocol,
        purposes=args.purposes,
        groups=args.groups,
        kinds=args.kinds
    )

    # go through all files, check if they are available on the filesystem
    good = []
    bad = []
    for obj in objects:
        if os.path.exists(obj.make_path(directory=args.directory)):
            good.append(obj)
        else:
            bad.append(obj)

    # report
    output = sys.stdout
    if args.selftest:
        from bob.db.base.utils import null
        output = null()

    if bad:
        for obj in bad:
            output.write('Cannot find file "%s"\n' % obj.make_path(directory=args.directory))
        output.write('%d files (out of %d) were not found at "%s"\n' % \
                     (len(bad), len(objects), args.directory))

    return 0


class Interface(BaseInterface):

    def name(self):
        return 'putvein'

    def files(self):
        return []

    def version(self):
        import pkg_resources  # part of setuptools
        return pkg_resources.require('bob.db.%s' % self.name())[0].version

    def type(self):
        return 'text'

    def add_commands(self, parser):
        """Add specific subcommands that the action "dumplist" can use"""

        from . import __doc__ as docs

        subparsers = self.setup_parser(parser, "PUT Vein Database", docs)

        from argparse import SUPPRESS

        db = Database()

        # add the dumplist command
        dump_message = "Dumps list of files based on your criteria"
        dump_parser = subparsers.add_parser('dumplist', help=dump_message)
        dump_parser.add_argument('-d', '--directory', dest="directory", default='', help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
        dump_parser.add_argument('-p', '--protocol', dest="protocol", default=None, help="limits the dump to a particular subset of the data that corresponds to the given protocol", choices=db.protocols)
        dump_parser.add_argument('-g', '--groups', dest="groups", default=None, help="if given, this value will limit the output files to those belonging to a particular group. (defaults to '%(default)s')", choices=db.groups)
        dump_parser.add_argument('-u', '--purposes', dest="purposes", default=None, help="if given, this value will limit the output files to those belonging to a particular purposes. (defaults to '%(default)s')", choices=db.purposes)
        dump_parser.add_argument('-k', '--kinds', dest="kinds", default=None, help="if given, this value will limit the output files to those belonging to a particular kind. (defaults to '%(default)s')", choices=db.kinds)
        dump_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
        dump_parser.set_defaults(func=dumplist) #action

        # add the checkfiles command
        check_message = "Check if the files exist, based on your criteria"
        check_parser = subparsers.add_parser('checkfiles', help=check_message)
        check_parser.add_argument('-d', '--directory', dest="directory", default='', help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
        check_parser.add_argument('-p', '--protocol', dest="protocol", default=None, help="limits the dump to a particular subset of the data that corresponds to the given protocol", choices=db.protocols)
        check_parser.add_argument('-g', '--groups', dest="groups", default=None, help="if given, this value will limit the output files to those belonging to a particular group. (defaults to '%(default)s')", choices=db.groups)
        check_parser.add_argument('-u', '--purposes', dest="purposes", default=None, help="if given, this value will limit the output files to those belonging to a particular purposes. (defaults to '%(default)s')", choices=db.purposes)
        check_parser.add_argument('-k', '--kinds', dest="kinds", default=None, help="if given, this value will limit the output files to those belonging to a particular kind. (defaults to '%(default)s')", choices=db.kinds)
        check_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
        check_parser.set_defaults(func=checkfiles) #action
