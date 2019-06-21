#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This script creates the VERA fingervein SQL database in a single pass.
"""

import os
import re
import csv
import pkg_resources

from .models import *


VERAFINGER_PATH = os.environ.get('VERAFINGER_PATH',
    '/path/to/root/of/vera/fingervein')


def add_clients(session, path, verbose):
  """Create client entries at the database"""

  metadata = os.path.join(path, 'metadata.csv')
  with open(metadata, 'rt') as f:
    header = None
    for row in csv.reader(f):
      if header is None:
        header = row
        continue
      id_, gender, age = row
      id_ = int(id_)
      age = int(age)

      # create client
      client = Client(id_, gender, age)
      session.add(client)

      if verbose:
        print("Created %s" % client)


def add_fingers(session, verbose):
  """Create finger entries at the database"""

  for client in session.query(Client):
    for side in Finger.side_choices:
      finger = Finger(client, side)
      session.add(finger)

      if verbose:
        print("Created %s" % finger)


def add_files(db_session, verbose):
  """Create file entries at the database"""

  for finger in db_session.query(Finger):
    for size in File.size_choices:
      for source in File.source_choices:
        for session in File.session_choices:
          file_ = File(size, source, finger, session)
          db_session.add(file_)
          if verbose: print("Created %s" % file_)


def retrieve_file(session, size, source, ref):
  """Retrieves the given File object from a full path"""

  bits = re.split(r'[-_/]', ref)
  # here is the outcome of this split:
  # [0] client-id
  # [1] gender (F or M)
  # [2] client-id
  # [3] side (L or R)
  # [4] session (1 or 2)
  return session.query(File).join(Finger,Client).filter(
    File.size==size, #full or cropped
    File.source==source, #bf or pa
    File.session==bits[4],
    Client.id==int(bits[0]),
    Finger.side==bits[3],
    ).one()


def add_bio_protocols(session, path, verbose):
  """Creates biometric/vulnerability analysis protocols entries at the database
  """

  protocol_dir = os.path.join(path, 'protocols', 'bio')

  for size in File.size_choices:

    for name in os.listdir(protocol_dir):
      if size == 'full':
        protocol = Protocol(name)
      else:
        protocol = Protocol('Cropped-' + name)
      session.add(protocol)
      if verbose:
        print("Created %s" % protocol)

      # training data
      train_filename = os.path.join(protocol_dir, name, 'train.txt')
      subset = Subset(protocol, 'train', 'train')
      session.add(subset)
      if verbose:
        print("Created %s" % subset)
      with open(train_filename, 'rt') as f:
        for row in f:
          # we ignore the client identifier as it can be derived from the file
          # name in the case of this dataset
          filename_ref, _ = row.strip().split()
          file_ = retrieve_file(session, size, 'bf', filename_ref)
          subset.files.append(file_)
          if verbose:
            print("Added %s to %s" % (file_, subset))

      # enrollment data
      models_filename = os.path.join(protocol_dir, name, 'models.txt')
      subset = Subset(protocol, 'dev', 'enroll')
      session.add(subset)
      if verbose:
        print("Created %s" % subset)
      with open(models_filename, 'rt') as f:
        for row in f:
          # we ignore the model and client identifier as they can be derived from
          # the file name in the case of this dataset
          filename_ref, _, _ = row.strip().split()
          file_ = retrieve_file(session, size, 'bf', filename_ref)
          subset.files.append(file_)
          if verbose:
            print("Added %s to %s" % (file_, subset))

      # probing data, including presentation attacks
      probes_filename = os.path.join(protocol_dir, name, 'probes.txt')
      bf_subset = Subset(protocol, 'dev', 'probe')
      session.add(bf_subset)
      if verbose:
        print("Created %s" % bf_subset)
      pa_subset = Subset(protocol, 'dev', 'attack')
      session.add(pa_subset)
      if verbose:
        print("Created %s" % pa_subset)
      with open(probes_filename, 'rt') as f:
        for row in f:
          # we ignore the client identifier as it can be derived from the file
          # name in the case of this dataset
          filename_ref, _ = row.strip().split()
          file_ = retrieve_file(session, size, 'bf', filename_ref)
          bf_subset.files.append(file_)
          if verbose:
            print("Added %s to %s" % (file_, bf_subset))
          file_ = retrieve_file(session, size, 'pa', filename_ref)
          pa_subset.files.append(file_)
          if verbose:
            print("Added %s to %s" % (file_, pa_subset))


def add_pad_protocols(session, path, verbose):
  """Creates presentation attack detection protocols entries at the database
  """

  protocol_dir = os.path.join(path, 'protocols', 'pad')

  # there are 2 protocols "full" and "cropped"
  for name in os.listdir(protocol_dir):
    protocol = PADProtocol(name)
    session.add(protocol)
    if verbose:
      print("Created %s" % protocol)

    for k in PADSubset.group_choices:
      filelist = os.path.join(protocol_dir, name, k + '.txt')
      bf_subset = PADSubset(protocol, k, 'real')
      session.add(bf_subset)
      if verbose:
        print("Created %s" % bf_subset)
      pa_subset = PADSubset(protocol, k, 'attack')
      session.add(pa_subset)
      if verbose:
        print("Created %s" % pa_subset)
      with open(filelist, 'rt') as f:
        for row in f:
          size, source, client_name, sample_name = row.strip().split('/')
          filename_ref = '/'.join((client_name, sample_name))
          file_ = retrieve_file(session, size, source, filename_ref)
          if source == 'bf':
            bf_subset.files.append(file_)
            if verbose:
              print("Added %s to %s" % (file_, bf_subset))
          else:
            pa_subset.files.append(file_)
            if verbose:
              print("Added %s to %s" % (file_, pa_subset))


def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock

  echo = args.verbose > 2 if args.verbose else False
  engine = create_engine_try_nolock(args.type, args.files[0], echo=echo)
  Base.metadata.create_all(engine)


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
  echo = args.verbose > 2 if args.verbose else False
  s = session_try_nolock(args.type, args.files[0], echo=echo)
  add_clients(s, args.directory, args.verbose)
  add_fingers(s, args.verbose)
  add_files(s, args.verbose)
  add_pad_protocols(s, args.directory, args.verbose)
  add_bio_protocols(s, args.directory, args.verbose)
  s.commit()
  s.close()


def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-d', '--directory', default=VERAFINGER_PATH, help="if given, use this path to search for protocol files [default: %(default)s]")
  parser.add_argument('-R', '--recreate', action='store_true',
    help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count',
    help='Do SQL operations in a verbose way')

  parser.set_defaults(func=create) #action
