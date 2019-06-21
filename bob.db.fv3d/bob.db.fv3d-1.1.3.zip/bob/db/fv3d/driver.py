#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Bob Database Driver entry-point for the 3D Fingervein database
"""

import os
import sys
import pkg_resources
from bob.db.base.driver import Interface as BaseInterface


def dumplist(args):
  """Dumps lists of files based on your criteria"""

  from .query import Database
  db = Database()

  r = db.objects(
      protocol=args.protocol,
      groups=args.group,
      purposes=args.purpose,
      model_ids=args.models,
      )

  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  for f in r:
    output.write('%s\n' % (f.make_path(args.directory, args.extension),))

  return 0


def checkfiles(args):
  """Checks existence of files based on your criteria"""

  from .query import Database
  db = Database()

  r = db.objects()

  # go through all files, check if they are available on the filesystem
  good = []
  bad = []
  for f in r:
    if os.path.exists(f.make_path(args.directory, args.extension)):
      good.append(f)
    else:
      bad.append(f)

  # report
  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  if bad:
    for f in bad:
      output.write('Cannot find file "%s"\n' % (f.make_path(args.directory, args.extension),))
    output.write('%d files (out of %d) were not found at "%s"\n' % \
      (len(bad), len(r), args.directory))

  return 0


class Interface(BaseInterface):


  def name(self):
    return 'fv3d'


  def version(self):
    return pkg_resources.require('bob.db.%s' % self.name())[0].version


  def files(self):
    basedir = pkg_resources.resource_filename(__name__, '')
    filelist = os.path.join(basedir, 'files.txt')
    with open(filelist, 'rt') as f:
      return [os.path.join(basedir, k.strip()) for k in \
          f.readlines() if k.strip()]


  def type(self):
    return 'sqlite'


  def add_commands(self, parser):

    from . import __doc__ as docs

    subparsers = self.setup_parser(parser,
        "3D Fingervein database", docs)

    # example: get the "create" action from a submodule
    from .create import add_command as create_command
    create_command(subparsers)

    # example: get the "dumplist" action from a submodule
    from .query import Database
    import argparse
    db = Database()

    parser = subparsers.add_parser('dumplist', help=dumplist.__doc__)
    parser.add_argument('-d', '--directory', default='', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', default='', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('-p', '--protocol', help="if given, limits the dump to a particular subset of the data that corresponds to the given protocol.", choices=db.protocol_names() if db.is_valid() else ())
    parser.add_argument('-u', '--purpose', help="if given, this value will limit the output files to those designed for the given purposes.", choices=db.purposes() if db.is_valid() else ())
    parser.add_argument('-m', '--models', type=str, help="if given, limits the dump to a particular model")
    parser.add_argument('-g', '--group', help="if given, this value will limit the output files to those belonging to a particular protocolar group.", choices=db.groups() if db.is_valid() else ())
    parser.add_argument('-c', '--class', dest='sclass', help="if given, this value will limit the output files to those belonging to the given classes.", choices=('client', 'impostor'))
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=dumplist) #action

    # the "checkfiles" action
    parser = subparsers.add_parser('checkfiles', help=checkfiles.__doc__)
    parser.add_argument('-d', '--directory', default='', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', default='.png', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=checkfiles) #action
