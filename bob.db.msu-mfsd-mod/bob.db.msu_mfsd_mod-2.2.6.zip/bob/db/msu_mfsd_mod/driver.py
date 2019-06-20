#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Sushil Bhattacharjee <sushil.bhattacharjee@idiap.ch>
#Tue 10 Mar 16:28:54 CET 2015

"""Bob Database Driver entry-point for modified protocol of MSU Mobile Face Spoofing Database.
"""

#import os
#import sys
#from bob.db.base.driver import Interface as BaseInterface
#from . import Database

import os
import sys
from bob.db.base.driver import Interface as BaseInterface


# Driver API
# ==========

def dumplist(args):
  """Dumps lists of files based on your criteria"""

  #from .__init__ import Database
  from .query import Database
  db = Database()

# objects = db.objects(group=args.group, cls=args.cls, quality=args.quality, types=args.attack_type)
  objects = db.objects(quality=args.quality, instrument=args.attack_type, fold=args.fold, group=args.group, cls=args.cls)


  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  for obj in objects:
    output.write('%s\n' % (obj.make_path(directory=args.directory, extension=args.extension),))

  return 0

def checkfiles(args):
  """Checks the existence of the files based on your criteria"""

  #from .__init__ import Database
  from .query import Database
  db = Database()

  #objects = db.objects(groups=args.group, cls=args.cls, qualities=args.quality, types=args.attack_type)
  objects = db.objects(quality=args.quality, instrument=args.attack_type, fold=args.fold, group=args.group, cls=args.cls)

  # go through all files, check if they are available on the filesystem
  good = []
  bad = []
  for obj in objects:
    if os.path.exists(obj.make_path(directory=args.directory, extension=args.extension)): good.append(obj)
    else: bad.append(obj)

  # report
  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  if bad:
    for obj in bad:
      output.write('Cannot find file "%s"\n' % (obj.make_path(directory=args.directory, extension=args.extension),))
    output.write('%d files (out of %d) were not found at "%s"\n' % \
        (len(bad), len(objects), args.directory))

  return 0

class Interface(BaseInterface):

  def name(self):
    return 'msu_mfsd_mod'

# OLD VERSION of files(), when db was not sql-based.
#  def files(self):
#    from pkg_resources import resource_filename
#    raw_files = (
##      'train_sub_list.txt',
##      'test_sub_list.txt',
##      'train_clients_1.txt',
##      'train_clients_2.txt',
##      'train_clients_3.txt',
##      'train_clients_4.txt',
##      'train_clients_5.txt',
##      'test_clients.txt',
#       'bob/db/msu_mfsd_mod/folds/clients_fold1.txt',
#       'bob/db/msu_mfsd_mod/folds/clients_fold2.txt',
#       'bob/db/msu_mfsd_mod/folds/clients_fold3.txt',
#       'bob/db/msu_mfsd_mod/folds/clients_fold4.txt',
#       'bob/db/msu_mfsd_mod/folds/clients_fold5.txt',
#       'bob/db/msu_mfsd_mod/folds/msu_mfsd_mod_realvids.txt',
#       'bob/db/msu_mfsd_mod/folds/msu_mfsd_mod_attackvids.txt',
#      )
#    return [resource_filename(__name__, k) for k in raw_files]

  def files(self):

    from pkg_resources import resource_filename
    raw_files = ('db.sql3',)
    return [resource_filename(__name__, k) for k in raw_files]


  def version(self):
    import pkg_resources  # part of setuptools
    return pkg_resources.require('bob.db.%s' % self.name())[0].version

  def type(self):
    return 'sqlite'

  def add_commands(self, parser):
    """Add specific subcommands that the action "dumplist" can use"""

    from . import __doc__ as docs

    subparsers = self.setup_parser(parser,
        "MSU Mobile Face Spoofing Database", docs)

    from argparse import SUPPRESS

    from .query import Database
    db = Database()


   # get the "create" action from a submodule
    from .create import add_command as create_command
    create_command(subparsers)


    # add the dumplist command
    dump_message = "Dumps list of files based on your criteria"
    dump_parser = subparsers.add_parser('dumplist', help=dump_message)
    dump_parser.add_argument('-d', '--directory', dest="directory", default='', help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
    dump_parser.add_argument('-e', '--extension', dest="extension", default='', help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")

    dump_parser.add_argument('-c', '--class', dest="cls", default=None, help="if given, limits the dump to a particular subset of the data that corresponds to the given class (defaults to '%(default)s')", choices=db.presentation_classes())
    dump_parser.add_argument('-f', '--fold', dest="fold", default=None, help="if given, limits the dump to a particular subset of the data that corresponds to the given fold (defaults to '%(default)s')", choices=db.folds())
    dump_parser.add_argument('-g', '--group', dest="group", default=None, help="if given, this value will limit the output files to those belonging to a particular group. (defaults to '%(default)s')", choices=db.groups())
    dump_parser.add_argument('-q', '--quality', dest="quality", default=None, help="if given, this value will limit the output files to those belonging to a particular quality of recording. (defaults to '%(default)s')", choices=db.qualities())
    dump_parser.add_argument('-t', '--type', dest="attack_type", default=None, help="if given, this value will limit the output files to those belonging to a particular type of attack. (defaults to '%(default)s')", choices=db.attack_instruments())

    dump_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
    dump_parser.set_defaults(func=dumplist) #action

    # add the checkfiles command
    check_message = "Check if the files exist, based on your criteria"
    check_parser = subparsers.add_parser('checkfiles', help=check_message)
    check_parser.add_argument('-d', '--directory', dest="directory", default='', help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
    check_parser.add_argument('-e', '--extension', dest="extension", default='', help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")

    check_parser.add_argument('-c', '--class', dest="cls", default=None, help="if given, limits the dump to a particular subset of the data that corresponds to the given class (defaults to '%(default)s')", choices=db.presentation_classes())
    check_parser.add_argument('-f', '--fold', dest="fold", default=None, help="if given, this value will limit the output files to those belonging to a particular fold. (defaults to '%(default)s')", choices=db.folds())
    check_parser.add_argument('-g', '--group', dest="group", default=None, help="if given, this value will limit the output files to those belonging to a particular group. (defaults to '%(default)s')", choices=db.groups())
    check_parser.add_argument('-q', '--quality', dest="quality", default=None, help="if given, this value will limit the output files to those belonging to a particular quality of recording. (defaults to '%(default)s')", choices=db.qualities())
    check_parser.add_argument('-t', '--type', dest="attack_type", default=None, help="if given, this value will limit the output files to those belonging to a particular type of attack. (defaults to '%(default)s')", choices=db.attack_instruments())

    check_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
    check_parser.set_defaults(func=checkfiles) #action



