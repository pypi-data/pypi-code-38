#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This script creates the KBOC16 database in a single pass.
"""

import os,string

from .models import *

# clients
userid_clients = range(1, 301)

def nodot(item):
  """Can be used to ignore hidden files, starting with the . character."""
  return item[0] != '.'

def add_clients(session, verbose):
  """Add clients to the ATVS Keystroke database."""
  for cid in userid_clients:
    if verbose>1: print("  Adding user '%s'" % (cid))
    session.add(Client(cid))


def add_files(session, imagedir, verbose):
  """Add files to the KBOC16 database."""

  def add_file(session, basename, userid, shotid, sessionid):
    """Parse a single filename and add it to the list."""
    session.add(File(userid, basename, sessionid, shotid))

  filenames = os.listdir(imagedir)
  for filename in filenames:
    basename, extension = os.path.splitext(filename)
    if extension == db_file_extension:
      if verbose>1: print("  Adding file '%s'..." % (basename))
      parts = string.split(basename, "_")
      shotid = int(parts[1])
      userid = int(parts[0][-3:])
      if shotid <= 4:
        sessionid = 1
      elif shotid > 4:
        sessionid = 2
        shotid = shotid - 4
      add_file(session, basename, userid, shotid, sessionid)


def add_protocols(session, verbose):
  """Adds protocols"""

  # 1. DEFINITIONS
  enroll_session = [1]
  client_probe_session = [2]
  protocols = ['A','D']
  client_ids_protD = range(1,101)

  # 2. ADDITIONS TO THE SQL DATABASE
  protocolPurpose_list = [('eval', 'enrol'), ('eval', 'probe')]
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
      print('%s %s %s' % (p.id, purpose[0], purpose[1]))
      pu = ProtocolPurpose(p.id, purpose[0], purpose[1])
      if verbose>1: print("  Adding protocol purpose ('%s','%s')..." % (purpose[0], purpose[1]))
      session.add(pu)
      session.flush()
      session.refresh(pu)

      # Add files attached with this protocol purpose
      if(key == 0): #test enrol
        if proto == 'D':
          q = session.query(File).join(Client).filter(Client.id.in_(client_ids_protD)).filter(File.session_id.in_(enroll_session))
        else:
          q = session.query(File).join(Client).filter(File.session_id.in_(enroll_session))
        for k in q:
          if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
          pu.files.append(k)

      elif(key == 1): #test probe
        if (proto == 'D'):
          q = session.query(File).join(Client).filter(Client.id.in_(client_ids_protD)).filter(File.session_id.in_(client_probe_session))
        else:
          q = session.query(File).join(Client).filter(File.session_id.in_(client_probe_session))
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
  parser.add_argument('-D', '--imagedir', metavar='DIR', default='/idiap/group/biometric/databases/kboc16', help="Change the relative path to the directory containing the images of the KBOC16 database.")

  parser.set_defaults(func=create) #action
