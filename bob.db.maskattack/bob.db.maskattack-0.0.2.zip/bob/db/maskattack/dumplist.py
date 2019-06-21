#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <nesli.erdogmus@idiap.ch>
# Mon 25 Feb 16:12:47 2013

"""Dumps lists of files.
"""

import os
import sys

# Driver API
# ==========

def dumplist(args):
  """Dumps lists of files based on your criteria"""

  from .query import Database
  db = Database()

  r = db.objects(
      protocol=args.protocol, 
      purposes=args.purposes,
      client_ids=args.client,
      sets=args.sets, 
      classes=args.classes,
      )

  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  for f in r:
    output.write('%s\n' % (f.make_path(args.directory, args.extension),))

  return 0

def add_command(subparsers):
  """Add specific subcommands that the action "dumplist" can use"""

  from argparse import SUPPRESS

  parser = subparsers.add_parser('dumplist', help=dumplist.__doc__)

  from .query import Database

  db = Database()

  if not db.is_valid():
    protocols = ('waiting','for','database','creation')
    clients = tuple()
  else:
    protocols = [k.name for k in db.protocols()]
    clients = [k.id for k in db.clients()]

  parser.add_argument('-d', '--directory', dest="directory", default=None,   help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
  parser.add_argument('-e', '--extension', dest="extension", default=None,   help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")
  parser.add_argument('-x', '--protocol',  dest="protocol",  default=None,   help="if given, this value will limit the output files to those for a given protocol. (defaults to '%(default)s')", choices=protocols)
  parser.add_argument('-p', '--purposes',  dest="purposes",  default=None,   help="if given, this value will limit the output files to those for a given purpose. (defaults to '%(default)s')", choices=db.purposes())
  parser.add_argument('-i', '--client',    dest="client",    default=None,   help="if given, this value will limit the output files to those of a given client id. (defaults to '%(default)s')", choices=clients, type=int)
  parser.add_argument('-s', '--sets',      dest="sets",      default=None,   help="if given, this value will limit the output files to those for a given set. (defaults to '%(default)s')", choices=db.sets())
  parser.add_argument('-c', '--classes',   dest="classes",   default=None, help="if given, this value will limit the output files to those for a given class. (defaults to '%(default)s')", choices=('client', 'impostor'))
  parser.add_argument('--self-test',       dest="selftest",  default=False, action='store_true', help=SUPPRESS)

  parser.set_defaults(func=dumplist) #action
