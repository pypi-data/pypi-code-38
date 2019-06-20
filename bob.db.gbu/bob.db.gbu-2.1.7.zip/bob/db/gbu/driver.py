#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Fri May 11 17:20:46 CEST 2012
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

"""Commands the GBU database can respond to.
"""

import os
import sys
import tempfile, shutil
import argparse

from bob.db.base import utils
from bob.db.base.driver import Interface as BaseInterface

def dumplist(args):
  """Dumps lists of files based on your criteria"""

  from .query import Database
  db = Database()

  r = db.objects(
      groups=args.group,
      subworld=args.subworld,
      protocol=args.protocol,
      purposes=args.purpose
  )

  output = sys.stdout
  if args.selftest:
    output = utils.null()

  for file in r:
    output.write('%s\n' % file.make_path(args.directory, args.extension))

  return 0

def checkfiles(args):
  """Checks existence of files based on your criteria"""

  from .query import Database
  db = Database()

  objects = db.objects()

  # go through all files, check if they are available on the filesystem
  good = {}
  bad = {}
  for file in objects:
    if os.path.exists(file.make_path(args.directory, args.extension)):
      good[file.id] = file
    else:
      bad[file.id] = file

  # report
  output = sys.stdout
  if args.selftest:
    output = utils.null()

  if bad:
    for id, file in bad.items():
      output.write('Cannot find file "%s"\n' % (file.make_path(args.directory, args.extension),))
    output.write('%d files (out of %d) were not found at "%s"\n' % \
        (len(bad), len(objects), args.directory))

  return 0


def copy_image_files(args):
  """This function scans the given input directory for the images
  required by this database and creates a new directory with the
  required sub-directory structure, by copying or linking the images"""

  if os.path.exists(args.new_image_directory):
    print("Directory", args.new_image_directory, "already exists, please choose another one.")
    return
  # collect the files in the given directory
  from .create import collect_files
  print("Collecting image files from directory", args.original_image_directory)
  filelist, dirlist = collect_files(args.original_image_directory, args.original_image_extension, args.sub_directory)

  print("Done. Found", len(filelist), "image files.")
  # get the files of the database
  from .query import Database
  db = Database()
  db_files = db.objects()

  # create a temporary structure for faster access
  temp_dict = {}
  for file in db_files:
    temp_dict[os.path.basename(file.path)[0]] = file

  command = os.symlink if args.soft_link else shutil.copy
  print("Copying (or linking) files to directory", args.new_image_directory)
  # now, iterate through the detected files
  for index in range(len(filelist)):
    file_wo_extension = os.path.splitext(filelist[index])[0]
    if file_wo_extension in temp_dict:
      # get the files
      old_file = os.path.join(args.original_image_directory, dirlist[index], filelist[index])
      new_file = temp_dict[file_wo_extension].make_path(args.new_image_directory, '.jpg')
      new_dir = os.path.dirname(new_file)
      if not os.path.exists(new_dir):
        os.makedirs(new_dir)

      # copy or link
      assert not os.path.exists(new_file)
      command(old_file, new_file)

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
    return 'gbu'

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
       "The GBU database", docs)

    # get the "create" action from a submodule
    from .create import add_command as create_command
    create_command(subparsers)

    from .models import Protocol, Subworld

    # the "dumplist" action
    parser = subparsers.add_parser('dumplist', help=dumplist.__doc__)
    parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('-g', '--group', help="if given, this value will limit the output files to those belonging to a particular group.", choices=('world', 'dev'))
    parser.add_argument('-s', '--subworld', help="if given, limits the dump to a particular subworld of the data.", choices=Subworld.subworld_choices)
    parser.add_argument('-p', '--protocol', help="if given, limits the dump to a particular subset of the data that corresponds to the given protocol.", choices=Protocol.protocol_choices)
    parser.add_argument('-u', '--purpose', help="if given, this value will limit the output files to those designed for the given purposes.", choices=Protocol.purpose_choices)
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=dumplist) #action

    # the "checkfiles" action
    parser = subparsers.add_parser('checkfiles', help=checkfiles.__doc__)
    parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=checkfiles) #action

    # the "copy-image-files" action
    parser = subparsers.add_parser('copy-image-files', help=copy_image_files.__doc__)
    parser.add_argument('-d', '--original-image-directory', metavar='DIR', required=True, help="Specify the image directory containing the MBGC-V1 images.")
    parser.add_argument('-e', '--original-image-extension', metavar='EXT', default = '.jpg', help="The extension of the images in the database.")
    parser.add_argument('-n', '--new-image-directory', metavar='DIR', required=True, help="Specify the image directory where the images should be copied to.")
    parser.add_argument('-s', '--sub-directory', metavar='DIR', help="To speed up the search process you might define a sub-directory that is scanned, e.g., 'Original'.")
    parser.add_argument('-l', '--soft-link', action='store_true', help="If selected, the images will be linked rather than copied.")
    parser.set_defaults(func=copy_image_files) #action

    # adds the "reverse" command
    parser = subparsers.add_parser('reverse', help=reverse.__doc__)
    parser.add_argument('path', nargs='+', help="one or more path stems to look up. If you provide more than one, files which cannot be reversed will be omitted from the output.")
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=reverse) #action

    # adds the "path" command
    parser = subparsers.add_parser('path', help=path.__doc__)
    parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('id', type=int, nargs='+', help="one or more file ids to look up. If you provide more than one, files which cannot be found will be omitted from the output. If you provide a single id to lookup, an error message will be printed if the id does not exist in the database. The exit status will be non-zero in such case.")
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=path) #action

