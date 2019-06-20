#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Fri 20 May 17:00:50 2011
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""This script creates the BANCA database in a single pass.
"""

import os

from .models import *

def nodot(item):
  """Can be used to ignore hidden files, starting with the . character."""
  return item[0] != '.'

def add_files(session, imagedir, verbose):
  """Add files (and clients) to the BANCA database."""

  def add_file(session, subdir, filename, client_dict, verbose):
    """Parse a single filename and add it to the list.
       Also add a client entry if not already in the database."""

    v = os.path.splitext(os.path.basename(filename))[0].split('_')
    if not (v[0] in client_dict):
      if (v[2] == 'wm'):
        v[2] = 'world'
      session.add(Client(int(v[0]), v[1], v[2], v[5]))
      client_dict[v[0]] = True
    session_id = int(v[3].split('s')[1])
    base_path = os.path.join(subdir, os.path.basename(filename).split('.')[0])
    if verbose>1: print("  Adding file '%s'..." %(base_path, ))
    session.add(File(int(v[0]), base_path, v[4], v[6], session_id))

  if verbose: print("Adding files...")
  subdir_list = list(filter(nodot, os.listdir(imagedir)))
  client_dict = {}
  for subdir in subdir_list:
    file_list = list(filter(nodot, os.listdir(os.path.join(imagedir, subdir))))
    for filename in file_list:
      add_file(session, subdir, os.path.join(imagedir, filename), client_dict, verbose)


def add_annotations(session, annotdir, verbose):
  """Reads the annotation files and adds the annotations to the .sql3 database."""

  def read_annotation(filename, file_id):
    # read the eye positions, which are stored as four integers in one line
    line = open(filename, 'r').readline()
    positions = line.split()
    assert len(positions) == 4
    return Annotation(file_id, positions)

  # iterate though all stored images and try to access the annotations
  session.flush()
  if verbose: print("Adding annotations...")
  files = session.query(File)
  for f in files:
    annot_file = f.make_path(annotdir, '.pos')
    if os.path.exists(annot_file):
      if verbose>1: print("  Adding annotation '%s'..." %(annot_file, ))
      session.add(read_annotation(annot_file, f.id))
    else:
      print("Could not locate annotation file '%s'" % annot_file)


def add_subworlds(session, verbose):
  """Adds splits in the world set, based on the client ids"""

  # one third and two thirds
  snames = ["onethird", "twothirds"]
  slist = [ [9003, 9005, 9027, 9033, 9035, 9043, 9049, 9053, 9055, 9057],
            [9001, 9007, 9009, 9011, 9013, 9015, 9017, 9019, 9021, 9023,
             9025, 9029, 9031, 9037, 9039, 9041, 9045, 9047, 9051, 9059] ]
  for k in range(len(snames)):
    if verbose: print("Adding subworld '%s'" %(snames[k], ))
    su = Subworld(snames[k])
    session.add(su)
    session.flush()
    session.refresh(su)
    l = slist[k]
    for c_id in l:
      if verbose>1: print("  Adding client '%d' to subworld '%s'..." %(c_id, snames[k]))
      su.clients.append(session.query(Client).filter(Client.id == c_id).first())

def add_protocols(session, verbose):
  """Adds protocols"""

  # 1. DEFINITIONS
  # Numbers in the lists correspond to session identifiers
  protocol_definitions = {}

  # Protocol Mc
  enroll = [1]
  probe_c = [2, 3, 4]
  probe_i = [1, 2, 3, 4]
  protocol_definitions['Mc'] = [enroll, probe_c, probe_i]

  # Protocol Md
  enroll = [5]
  probe_c = [6, 7, 8]
  probe_i = [5, 6, 7, 8]
  protocol_definitions['Md'] = [enroll, probe_c, probe_i]

  # Protocol Ma
  enroll = [9]
  probe_c = [10, 11, 12]
  probe_i = [9, 10, 11, 12]
  protocol_definitions['Ma'] = [enroll, probe_c, probe_i]

  # Protocol Ud
  enroll = [1]
  probe_c = [6, 7, 8]
  probe_i = [5, 6, 7, 8]
  protocol_definitions['Ud'] = [enroll, probe_c, probe_i]

  # Protocol Ua
  enroll = [1]
  probe_c = [10, 11, 12]
  probe_i = [9, 10, 11, 12]
  protocol_definitions['Ua'] = [enroll, probe_c, probe_i]

  # Protocol P
  enroll = [1]
  probe_c = [2, 3, 4, 6, 7, 8, 10, 11, 12]
  probe_i = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
  protocol_definitions['P'] = [enroll, probe_c, probe_i]

  # Protocol G
  enroll = [1, 5, 9]
  probe_c = [2, 3, 4, 6, 7, 8, 10, 11, 12]
  probe_i = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
  protocol_definitions['G'] = [enroll, probe_c, probe_i]

  # 2. ADDITIONS TO THE SQL DATABASE
  protocolPurpose_list = [('world', 'train'), ('dev', 'enroll'), ('dev', 'probe'), ('eval', 'enroll'), ('eval', 'probe')]
  for proto in protocol_definitions:
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
      client_group = ""
      if(key == 0): client_group = "world"
      elif(key == 1 or key == 2): client_group = "g1"
      elif(key == 3 or key == 4): client_group = "g2"
      session_list = []
      session_list_i = []
      if(key == 1 or key == 3):
        session_list = protocol_definitions[proto][0]
      elif(key == 2):
        session_list = protocol_definitions[proto][1]
        session_list_i = protocol_definitions[proto][2]
      elif(key == 4):
        session_list = protocol_definitions[proto][1]
        session_list_i = protocol_definitions[proto][2]

      # Adds 'regular' files (i.e. 'world', 'enroll', 'probe client')
      if not session_list:
        q = session.query(File).join(Client).filter(Client.sgroup == client_group).\
              order_by(File.id)
        for k in q:
          if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
          pu.files.append(k)
      else:
        for sid in session_list:
          q = session.query(File).join(Client).filter(Client.sgroup == client_group).\
                filter(and_(File.session_id == sid, File.client_id == File.claimed_id)).\
                order_by(File.id)
          for k in q:
            if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
            pu.files.append(k)

      # Adds impostors if required
      if session_list_i:
        for sid in session_list_i:
          q = session.query(File).join(Client).filter(Client.sgroup == client_group).\
                filter(and_(File.session_id == sid, File.client_id != File.claimed_id)).\
                order_by(File.id)
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
  s = session_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
  add_files(s, args.imagedir, args.verbose)
  add_annotations(s, args.annotdir, args.verbose)
  add_subworlds(s, args.verbose)
  add_protocols(s, args.verbose)
  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', help='Do SQL operations in a verbose way')
  parser.add_argument('-D', '--imagedir', metavar='DIR', default='/idiap/group/biometric/databases/banca/english/images/images/', help="Change the relative path to the directory containing the images of the BANCA database (defaults to %(default)s)")
  parser.add_argument('-A', '--annotdir', metavar='DIR', default='/idiap/group/biometric/annotations/banca/english/images/annotations/', help="Change the relative path to the directory containing the annotations of the BANCA database (defaults to %(default)s)")

  parser.set_defaults(func=create) #action
