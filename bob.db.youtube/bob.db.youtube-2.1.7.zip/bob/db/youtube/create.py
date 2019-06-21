#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This script creates the YouTube Faces database in a single pass.
"""

import os
import bob.db.base
import bob.io.base
import bob.io.matlab
import pkg_resources

from .models import *

def add_directories(session, verbose):
  """Adds files to the LFW database.
     Returns dictionaries with ids of the clients and ids of the files
     in the generated SQL tables"""

  # read the video_names file and the video_labels
  if verbose: print("Adding clients and files ...")
  with open(pkg_resources.resource_filename('bob.db.youtube', 'protocol/Youtube_names.txt')) as names:     # the video_names field -- exported to text file
    labels = bob.io.base.load(pkg_resources.resource_filename('bob.db.youtube', 'protocol/Youtube_labels.mat')) # the video_labels field -- exported to a single Matlab file
    # iterate over the video names
    for index, line in enumerate(names):
      assert len(line) > 0
      path = line.rstrip()
      client_id = int(labels[0,index])
      split_id = os.path.basename(path)

      # create client ?
      if index == 0 or client_id != labels[0, index-1]:
        client_name = os.path.dirname(path)
        if verbose > 1: print("  Adding client %s" % client_name)
        session.add(Client(client_id, client_name))

      # create file (or better: directory)
      session.add(Directory(file_id = index + 1, client_id = client_id, path = path))
      if verbose > 1: print("    Adding file %s" % path)


def add_pairs(session, verbose):
  """Adds the pairs for all protocols of the LFW database"""

  # read the splits filename
  if verbose: print("Adding pairs ...")
  splits = bob.io.base.load(pkg_resources.resource_filename('bob.db.youtube', 'protocol/Youtube_splits.mat')) # the Splits field -- exported to a single Matlab file
  session.flush()

  for fold in range(splits.shape[2]):
    protocol_name = 'fold%d' % (fold+1)
    if verbose: print("  Adding protocol %s" % protocol_name)
    for index in range(splits.shape[0]):
      enroll_id = int(splits[index, 0, fold])
      probe_id = int(splits[index, 1, fold])
      match_pair = int(splits[index, 2, fold]) == 1

      # get client ids for enroll and probe files
      enroll_client_id = session.query(Directory).filter(Directory.id == enroll_id).first().client_id
      probe_client_id = session.query(Directory).filter(Directory.id == probe_id).first().client_id

      session.add(Pair(protocol = protocol_name, enroll_id = enroll_id, probe_id = probe_id, enroll_client_id = enroll_client_id, probe_client_id = probe_client_id, is_match = match_pair))
      if verbose > 1: print("    Adding pair %d - %d (%s)" % (enroll_id, probe_id, str(match_pair)))


def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
  Client.metadata.create_all(engine)
  Directory.metadata.create_all(engine)
  Pair.metadata.create_all(engine)

# Driver API
# ==========

def create(args):
  """Creates or re-creates this database"""

  from bob.db.base.utils import session_try_nolock

  dbfile = args.files[0]

  if args.recreate:
    if args.verbose and os.path.exists(dbfile):
      print('unlinking %s...' % dbfile)
    if os.path.exists(dbfile): os.unlink(dbfile)

  if not os.path.exists(os.path.dirname(dbfile)):
    os.makedirs(os.path.dirname(dbfile))

  # the real work...
  create_tables(args)
  s = session_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
  add_directories(s, args.verbose)
  add_pairs(s, args.verbose)

  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help='If set, the current database is erased before writing into it.')
  parser.add_argument('-v', '--verbose', action='count', help='Do SQL operations in a verbose way?')

  parser.set_defaults(func=create) #action
