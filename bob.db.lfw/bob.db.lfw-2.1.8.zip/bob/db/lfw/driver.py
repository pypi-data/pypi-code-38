#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# @date: Thu May 24 10:41:42 CEST 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Commands the Labeled Faces in the Wild database can respond to.
"""

import os
import sys
from bob.db.base.driver import Interface as BaseInterface

# Driver API
# ==========

def dumplist(args):
  """Dumps lists of files based on your criteria"""

  from .query import Database
  db = Database()

  r = db.objects(
      protocol=args.protocol,
      groups=args.group,
      purposes=args.purpose
  )

  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  for f in r:
    output.write('%s\n' % f.make_path(args.directory, args.extension))

  return 0

def dumppairs(args):
  """Dumps lists of pairs of files based on your criteria"""

  from .query import Database
  db = Database()

  r = db.pairs(
      protocol=args.protocol,
      groups=args.group,
      classes=args.sclass
  )

  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  for p in r:
    output.write('%s -> %s\n' % (p.enroll_file.make_path(args.directory, args.extension), p.probe_file.make_path(args.directory, args.extension)))

  return 0

def checkfiles(args):
  """Checks lists of files based on your criteria"""

  from .query import Database
  db = Database()

  # go through all files, check if they are available on the filesystem
  good = {}
  bad = {}
  for protocol in db.m_valid_protocols:
    r = db.objects(protocol=protocol)

    for f in r:
      if os.path.exists(f.make_path(args.directory, args.extension)):
        good[f.id] = f
      else:
        bad[f.id] = f

  # report
  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  if bad:
    for id, f in bad.items():
      output.write('Cannot find file "%s"\n' % f.make_path(args.directory, args.extension))
    output.write('%d files (out of %d) were not found at "%s"\n' % \
        (len(bad), len(r), args.directory))

  return 0

def annotations(args):
  """Returns a list of file database identifiers given the path stems"""

  from .query import Database
  db = Database(annotation_type=args.annotation_type)

  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  f = db.files([args.id])
  if len(f) != 1:
    output.write('Cannot find file with id "%d" in database\n' % args.id)
    return 1
  a = db.annotations(f[0])
  for f in a: output.write('%s : (%3.2f, %3.2f)\n' % (f, a[f][0], a[f][1]))

  if not a: return 1

  return 0

def reverse(args):
  """Returns a list of file database identifiers given the path stems"""

  from .query import Database
  db = Database()

  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  r = db.reverse(args.path)
  for f in r: output.write('%s\n' % f.id)

  if not r: return 1

  return 0

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



class Interface(BaseInterface):

  def name(self):
    return 'lfw'

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
        "Labeled Faces in the Wild database", docs)

    # example: get the "create" action from a submodule
    from .create import add_command as create_command
    create_command(subparsers)

    from .query import Database
    import argparse
    db = Database()

    # the "dumplist" action
    parser = subparsers.add_parser('dumplist', help=dumplist.__doc__)
    parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('-p', '--protocol', default='view1', help="specifies the protocol for which the files should be dumped.", choices=db.m_valid_protocols)
    parser.add_argument('-g', '--group', help="if given, limits the dump to a particular group of the data.", choices=db.m_valid_groups)
    parser.add_argument('-u', '--purpose', help="if given, limits the dump to a particular purpose.", choices=db.m_valid_purposes)
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=dumplist) #action

    # the "dumppairs" action
    parser = subparsers.add_parser('dumppairs', help=dumplist.__doc__)
    parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('-p', '--protocol', default='view1', help="specifies the protocol for which the files should be dumped.", choices=db.m_valid_protocols)
    parser.add_argument('-g', '--group', help="if given, limits the dump to a particular group of the data.", choices=db.m_valid_groups)
    parser.add_argument('-c', '--class', dest='sclass', help="if given, limits the dump to a particular class of pairs.", choices=db.m_valid_classes)
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=dumppairs) #action

    # the "checkfiles" action
    parser = subparsers.add_parser('checkfiles', help=checkfiles.__doc__)
    parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=checkfiles) #action

    # adds the "annotations" command
    parser = subparsers.add_parser('annotations', help=reverse.__doc__)
    parser.add_argument('id', type=int, help="The File id for which to retrieve the annotations.")
    parser.add_argument('-a', '--annotation-type', choices=('idiap', 'funneled'), default='funneled', help='Choose, which kind of annotations should be retrieved.')
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=annotations) #action

    # adds the "reverse" command
    parser = subparsers.add_parser('reverse', help=reverse.__doc__)
    parser.add_argument('path', nargs='+', help="one or more path stems to look up. If you provide more than one, files which cannot be reversed will be omitted from the output.")
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=reverse) #action

    # adds the "path" command
    parser = subparsers.add_parser('path', help=path.__doc__)
    parser.add_argument('-d', '--directory', default='', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', default='', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('id', nargs='+', type=int, help="one or more file ids to look up. If you provide more than one, files which cannot be found will be omitted from the output. If you provide a single id to lookup, an error message will be printed if the id does not exist in the database. The exit status will be non-zero in such case.")
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=path) #action

