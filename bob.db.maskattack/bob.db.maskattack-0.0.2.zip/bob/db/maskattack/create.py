#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <nesli.erdogmus@idiap.ch>
# Mon 25 Feb 14:18:41 2013 

"""This script creates the 3d mask attack database in a single pass.
"""

import os
import fnmatch

from .models import *

def add_clients(session, datadir, verbose):
  """Add clients to the 3d mask attack database."""

  for id in range(1,18):
    if id < 8: 
      set = 'world'
    elif id < 13:
      set = 'dev'
    else:
      set = 'test'
    if verbose: print( "Adding client %d on '%s' set..." % (id, set))
    session.add(Client(id, set))

def add_files(session, datadir, verbose):
  """Add clients to the 3d mask attack database."""

  for filename in os.listdir(datadir):
    if filename.endswith('.hdf5'):
      path, extension = os.path.splitext(filename)
      tokens = os.path.splitext(path)[0].split('_')
      client_id = int(tokens[0])
      session_ = int(tokens[1])
      shot = int(tokens[2])
      if verbose: print( "Adding filename '%s' ..." % (path,))
      session.add(File(client_id, path, session_, shot))

def add_protocols(session, verbose):
  """Adds protocols"""

  protocol_name = 'verification'
  p = Protocol(protocol_name)
  # Add protocol
  if verbose: print( "Adding protocol %s..." % (protocol_name))
  session.add(p)
  session.flush()
  session.refresh(p)  
  
  # Add protocol purposes
  protocolPurpose_list = [('world', 'trainReal'), ('dev', 'enrol'), ('dev', 'probeReal'), ('dev', 'probeMask'), ('test', 'enrol'), ('test', 'probeReal'), ('test', 'probeMask')]
  for key in range(len(protocolPurpose_list)):
    purpose = protocolPurpose_list[key]
    
    # Add files attached with this protocol purpose
    client_set = ""
    if(key == 0): 
      client_set = "world"
      session_list = [1, 2]
    elif key in [1,2,3]: 
      client_set = "dev"
      session_list = [key]
    elif key in [4,5,6]: 
      client_set = "test"
      session_list = [key-3]
      
    pu = ProtocolPurpose(p.id, purpose[0], purpose[1], session_list.__str__())
    if verbose: print( " Adding protocol purpose ('%s','%s')..." % (purpose[0], purpose[1]))
    session.add(pu)
    session.flush()
    session.refresh(pu)

    # Adds 'protocol' files
    for sid in session_list:
      q = session.query(File).join(Client).filter(Client.set == client_set).\
            filter(File.session == sid).order_by(File.id)
      for k in q:
        if verbose: print( " Adding protocol file '%s'..." % (k.path))
        #pu.fixfiles.append(k)
        pu.files.append(k)
  
  protocol_name = 'classification'
  p = Protocol(protocol_name)
  # Add protocol
  if verbose: print( "Adding protocol %s..." % (protocol_name))
  session.add(p)
  session.flush()
  session.refresh(p)  
  
  # Add protocol purposes
  protocolPurpose_list = [('world', 'trainReal'), ('world', 'trainMask'), ('dev', 'classifyReal'), ('dev', 'classifyMask'), ('test', 'classifyReal'), ('test', 'classifyMask')]
  for key in range(len(protocolPurpose_list)):
    purpose = protocolPurpose_list[key]

     # Add files attached with this protocol purpose
    client_set = ""
    if(key == 0): 
      client_set = "world"
      session_list = [1, 2]
    elif(key == 1):
      client_set = "world"
      session_list = [3]
    elif(key == 2): 
      client_set = "dev"
      session_list = [1, 2]
    elif(key == 3): 
      client_set = "dev"
      session_list = [3]
    elif(key == 4): 
      client_set = "test"
      session_list = [1, 2]
    elif(key == 5): 
      client_set = "test"
      session_list = [3]
      
    pu = ProtocolPurpose(p.id, purpose[0], purpose[1], session_list.__str__())
    if verbose: print( " Adding protocol purpose ('%s','%s')..." % (purpose[0], purpose[1]))
    session.add(pu)
    session.flush()
    session.refresh(pu)

    # Adds 'protocol' files
    for sid in session_list:
      q = session.query(File).join(Client).filter(Client.set == client_set).\
            filter(File.session == sid).order_by(File.id)
      for k in q:
        if verbose: print( " Adding protocol file '%s'..." % (k.path))
        #pu.fixfiles.append(k)
        pu.files.append(k)

def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2))
  Base.metadata.create_all(engine)

# Driver API
# ==========

def create(args):
  """Creates or re-creates this database"""

  from bob.db.utils import session_try_nolock

  dbfile = args.files[0]

  if args.recreate: 
    if args.verbose and os.path.exists(dbfile):
      print('unlinking %s...' % dbfile)
    if os.path.exists(dbfile): os.unlink(dbfile)

  if not os.path.exists(os.path.dirname(dbfile)):
    os.makedirs(os.path.dirname(dbfile))

  # the real work...
  create_tables(args)
  s = session_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2))
  add_clients(s, args.datadir, args.verbose)
  add_files(s, args.datadir, args.verbose)
  add_protocols(s, args.verbose)
  s.commit()
  s.close()

  return 0
  
def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', default=False,
      help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count',
      help="Do SQL operations in a verbose way")
  parser.add_argument('-D', '--datadir', action='store', 
      default='/idiap/project/tabularasa/3D Mask Attack/Data',
      metavar='DIR',
      help="Change the relative path to the directory containing the data (defaults to %(default)s)")
  
  parser.set_defaults(func=create) #action
