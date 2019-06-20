#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This script creates the BiosecurId database in a single pass.
"""

import os

from .models import *

# clients
userid_training = range(1001,1151)
userid_dev_clients = range(1151, 1289)
userid_dev_impostors = range(1289, 1301)
userid_eval_clients = range(1301, 1391)
userid_eval_impostors = range(1391, 1401)


def nodot(item):
  """Can be used to ignore hidden files, starting with the . character."""
  return item[0] != '.'

def add_clients(session, verbose):
  """Add clients to the BiosecurId database."""
  users_list = (userid_training, userid_dev_clients, userid_dev_impostors, userid_eval_clients, userid_eval_impostors)
  group_choices = ('world', 'clientDev','impostorDev','clientEval','impostorEval')

  if verbose: print("Adding users...")
  for g, group in enumerate(group_choices):
    for cid in users_list[g]:
      if verbose>1: print("  Adding user '%d' on '%s' group..." % (cid,group))
      session.add(Client(cid, group))



def add_files(session, imagedir, verbose):
  """Add files to the BiosecurId database."""

  def add_file(session, basename, userdir, sessiondir):
    """Parse a single filename and add it to the list."""
    shotid = int(basename[-1])
    session.add(File(int(userdir[-4:]), os.path.join(userdir, sessiondir, basename), int(sessiondir[-1]), shotid))


  for userdir in os.listdir(imagedir):
    sdirs = os.listdir(os.path.join(imagedir,userdir))
    sessiondirs = [v for v in sdirs if os.path.isdir(os.path.join(imagedir,userdir,v))]

    for sessiondir in sessiondirs:
      #if verbose: print("Adding files of sub-dir '%s'..." % subdir)

      filenames = os.listdir(os.path.join(imagedir,userdir,sessiondir))
      for filename in filenames:
        basename, extension = os.path.splitext(filename)
        if extension == '.bmp' and 'fa' in basename:
          if verbose>1: print("  Adding file '%s'..." % (basename))
          add_file(session, basename, userdir, sessiondir)




def add_protocols(session, verbose):
  """Adds protocols"""

  # 1. DEFINITIONS
  enroll_session = [1, 2]
  client_probe_session = [3, 4]
  protocols = ['A']

  # 2. ADDITIONS TO THE SQL DATABASE
  protocolPurpose_list = [('world', 'train'), ('dev', 'enrol'), ('dev', 'probe'), ('eval', 'enrol'), ('eval', 'probe')]
  for proto in protocols:
    p = Protocol(proto)
    # Add protocol
    if verbose: print("Adding protocol %s..." % (proto))
    session.add(p)
    session.flush()
    session.refresh(p)

    # Add protocol purposes
    for key in range(len(protocolPurpose_list)):
      purpose = protocolPurpose_list[key]
      pu = ProtocolPurpose(p.id, purpose[0], purpose[1])
      if verbose>1: print("  Adding protocol purpose ('%s','%s')..." % (purpose[0], purpose[1]))
      session.add(pu)
      session.flush()
      session.refresh(pu)

      # Add files attached with this protocol purpose
      if(key == 0): # world
        q = session.query(File).join(Client).filter(Client.sgroup == 'world')
        for k in q:
          if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
          pu.files.append(k)

      elif(key == 1): #dev enrol
        q = session.query(File).join(Client).filter(Client.sgroup == 'clientDev').filter(File.session_id.in_(enroll_session))
        for k in q:
          if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
          pu.files.append(k)

      elif(key == 2): #dev probe
        q = session.query(File).join(Client).filter(Client.sgroup == 'clientDev').filter(File.session_id.in_(client_probe_session))
        for k in q:
          if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
          pu.files.append(k)
        q = session.query(File).join(Client).filter(Client.sgroup == 'impostorDev')
        for k in q:
          if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
          pu.files.append(k)

      elif(key == 3): #test enrol
        q = session.query(File).join(Client).filter(Client.sgroup == 'clientEval').filter(File.session_id.in_(enroll_session))
        for k in q:
          if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
          pu.files.append(k)

      elif(key == 4): #test probe
        q = session.query(File).join(Client).filter(Client.sgroup == 'clientEval').filter(File.session_id.in_(client_probe_session))
        for k in q:
          if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
          pu.files.append(k)
        q = session.query(File).join(Client).filter(Client.sgroup == 'impostorEval')
        for k in q:
          if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
          pu.files.append(k)


def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock
  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
  Base.metadata.create_all(engine)

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
  s = session_try_nolock(args.type, dbfile, echo=(args.verbose > 2))
  add_clients(s, args.verbose)
  add_files(s, args.imagedir, args.verbose)
  add_protocols(s, args.verbose)
  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', help="Do SQL operations in a verbose way?")
  parser.add_argument('-D', '--imagedir', metavar='DIR', default='/Users/martagomezbarrero/Documents/BiosecurID/data/', help="Change the relative path to the directory containing the images of the BiosecurID database.")

  parser.set_defaults(func=create) #action
