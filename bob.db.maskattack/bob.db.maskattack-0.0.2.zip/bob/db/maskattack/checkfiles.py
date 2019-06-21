#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <nesli.erdogmus@idiap.ch>
# Mon 25 Feb 11:02:33 2013

"""Checks for installed files.
"""

import os
import sys

# Driver API
# ==========

def checkfiles(args):
  """Checks existence files based on your criteria"""

  from .query import Database
  db = Database()

  r = db.objects(
      protocol=args.protocol, 
      purposes=args.purposes,
      client_ids=args.client_ids,
      sets=args.sets, 
      classes=args.classes,
      )

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

def add_command(subparsers):
  """Add specific subcommands that the action "checkfiles" can use"""

  from argparse import SUPPRESS

  parser = subparsers.add_parser('checkfiles', help=checkfiles.__doc__)

  from .query import Database

  db = Database()

  if not db.is_valid():
    protocols = ('waiting','for','database','creation')
    clients = tuple()
  else:
    protocols = [k.name for k in db.protocols()]
    clients = [k.id for k in db.clients()]

  parser.add_argument('-d', '--directory', dest="directory", default=None,   help="if given, this path will be prepended to every entry checked (defaults to '%(default)s')")
  parser.add_argument('-e', '--extension', dest="extension", default=None,   help="if given, this extension will be appended to every entry checked (defaults to '%(default)s')")
  parser.add_argument('-x', '--protocol',  dest="protocol",  default=None,   help="if given, this value will limit the check for files to those for a given protocol. (defaults to '%(default)s')", choices=protocols)
  parser.add_argument('-p', '--purposes',  dest="purposes",  default=None,   help="if given, this value will limit the check for files to those for a given purpose. (defaults to '%(default)s')", choices=db.purposes())
  parser.add_argument('-i', '--client_ids',dest="client_ids",default=None,   help="if given, this value will limit the check for files to those of a given client id. (defaults to '%(default)s')", choices=clients)
  parser.add_argument('-s', '--sets',      dest="sets",      default=None,   help="if given, this value will limit the check for files to those for a given set. (defaults to '%(default)s')", choices=db.sets())
  parser.add_argument('-c', '--classes',   dest="classes",   default=None, help="if given, this value will limit the check for files to those for a given class. (defaults to '%(default)s')", choices=('client', 'impostor'))
  parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)

  parser.set_defaults(func=checkfiles) #action
