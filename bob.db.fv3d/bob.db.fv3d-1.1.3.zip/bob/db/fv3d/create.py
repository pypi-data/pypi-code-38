#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This script creates the 3D Fingervein SQL database in a single pass.
"""

import os
import re
import csv
import pkg_resources

from .models import *
from sqlalchemy.orm.exc import NoResultFound


def add_clients(session, verbose):
  """Create client entries at the database"""

  metadata = pkg_resources.resource_filename(__name__, os.path.join('data',
    'metadata.csv'))
  with open(metadata, 'rt') as f:
    header = None
    for row in csv.reader(f):
      if header is None:
        header = row
        continue
      id_, age, gender, skin, occ = row
      id_ = int(id_)
      age = int(age)

      # create client
      client = Client(id_, gender, age, skin, occ)
      session.add(client)

      if verbose:
        print("Created %s" % client)


FILENAME_RE = re.compile(r'^(?P<id>\d{3})\-(?P<age>\d{3})\-(?P<gender>[fm])(?P<skin>[1-6x])(?P<occ>[0-9x])(?P<side>[lr])(?P<finger>[timlr])(?P<session>[1-3])(?P<attempt>[1-5])(?P<snap>[1-5])(?P<cam>[1-3S])$')

def try_get_metadata(path):
  '''Returns the metadata from a path or ``None`` if no match occurs'''

  m = FILENAME_RE.match(os.path.basename(path))

  if m is None: return m

  return {
      'id': int(m.group('id')),
      'age': int(m.group('age')),
      'gender': m.group('gender'),
      'skin': m.group('skin'),
      'occ': m.group('occ'),
      'side': m.group('side'),
      'finger': m.group('finger'),
      'session': str(int(m.group('session'))),
      'attempt': str(int(m.group('attempt'))),
      'snap': str(int(m.group('snap'))),
      'cam': m.group('cam'),
      }



def add_files(db_session, verbose):
  """Create file entries at the database"""


  dir_re = re.compile(r'^(?P<id>\d{3})$')

  fname = pkg_resources.resource_filename(__name__, os.path.join('data',
    'files.txt'))
  with open(fname, 'rb') as flist:
    for f in flist:
      info = try_get_metadata(f.strip().decode())

      # checks if the finger with the specifications is there/unique
      try:
        finger = db_session.query(Finger).join(Client).filter(
          Client.id==info['id'],
          Finger.side==info['side'],
          Finger.name==info['finger'],
          ).one()
      except NoResultFound as e:
        # creates the missing finger
        client = db_session.query(Client).filter(Client.id==info['id']).one()
        finger = Finger(client, info['side'], info['finger'])
        db_session.add(finger)
        if verbose:
          print("Created %s" % finger)

      # associates file to finger
      file_ = File(finger, info['session'], info['attempt'], info['snap'],
          info['cam'])
      db_session.add(file_)

      if verbose:
        print("Created %s" % file_)


def retrieve_file(session, ref):
  """Retrieves the given File object from a full path"""

  info = try_get_metadata(ref)
  return session.query(File).join(Finger,Client).filter(
      Client.id==info['id'],
      Finger.name==info['finger'],
      Finger.side==info['side'],
      File.session==info['session'],
      File.attempt==info['attempt'],
      File.snapshot==info['snap'],
      File.camera==info['cam'],
      ).one()


def add_protocols(session, verbose):
  """Create protocol entries at the database"""

  protocol_dir = pkg_resources.resource_filename(__name__, os.path.join('data',
    'protocols'))

  for name in os.listdir(protocol_dir):
    protocol = Protocol(name)
    session.add(protocol)
    if verbose:
      print("Created %s" % protocol)

    # training data
    train_filename = os.path.join(protocol_dir, name, 'train.txt')
    with open(train_filename, 'rb') as f:
      for filename in f:
        file_ = retrieve_file(session, filename.strip().decode())
        protocol.training_set.append(file_)
        if verbose:
          print("Added %s to %s" % (file_, protocol))

    # enrollment data
    models_filename = os.path.join(protocol_dir, name, 'dev-models.txt')
    with open(models_filename, 'rb') as f:
      for row in f:
        filename, model_ref = row.split()
        file_ = retrieve_file(session, filename.decode())
        model = session.query(Model).filter(Model.name==model_ref.decode(),
            Model.protocol==protocol)
        if model.count() == 0:
          model = Model(model_ref.decode(), 'dev', file_.finger, protocol)
          if verbose:
            print("Created model %s" % (model,))
        else:
          model = model.one()
        model.files.append(file_)
        if verbose:
          print("Added %s to %s" % (file_, model))

    # probing data
    probes_filename = os.path.join(protocol_dir, name, 'dev-probes.txt')
    with open(probes_filename, 'rb') as f:
      for filename in f:
        file_ = retrieve_file(session, filename.decode())
        probe = Probe('dev', protocol, file_)
        session.add(probe)
        if verbose:
          print("Created %s" % probe)


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
  add_clients(s, args.verbose)
  add_files(s, args.verbose)
  add_protocols(s, args.verbose)
  s.commit()
  s.close()


def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true',
    help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count',
    help='Do SQL operations in a verbose way')

  parser.set_defaults(func=create) #action
