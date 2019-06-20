#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
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

"""This script creates the Biosecure database in a single pass.
"""

import os

from .models import *

def nodot(item):
  """Can be used to ignore hidden files, starting with the . character."""
  return item[0] != '.'

def add_clients(session, verbose):
  """Add clients to the Biosecure database."""

  # world
  group_world = 'world'
  list_world = [  3,   5,  10,  12,  13,  14,  15,  17,  23,  24,
                 29,  33,  36,  37,  38,  39,  42,  47,  58,  62,
                 64,  73,  78,  80,  81,  82,  83,  85,  89,  93,
                102, 104, 107, 108, 109, 111, 112, 117, 119, 123,
                126, 130, 133, 137, 138, 143, 146, 147, 150, 152,
                154, 155, 156, 158, 160, 163, 164, 176, 178, 180,
                183, 196, 198, 199, 200, 201, 203, 206, 209, 210]
  # dev
  group_dev = 'dev'
  list_dev =   [  6,   7,  16,  18,  19,  20,  21,  22,  25,  27,
                 28,  32,  40,  41,  49,  50,  52,  54,  55,  60,
                 63,  67,  68,  69,  70,  75,  76,  79,  84,  88,
                 92,  94,  96,  97,  98,  99, 103, 105, 115, 118,
                120, 121, 122, 124, 127, 129, 131, 134, 135, 136,
                141, 142, 145, 153, 157, 159, 165, 166, 168, 169,
                170, 172, 175, 184, 185, 190, 193, 194, 204, 208]
  # eval
  group_eval = 'eval'
  list_eval =   [  1,   2,   4,   8,   9,  11,  26,  30,  31,  34,
                  35,  43,  44,  45,  46,  48,  51,  53,  56,  57,
                  59,  61,  65,  66,  71,  72,  74,  77,  86,  87,
                  90,  91,  95, 100, 101, 106, 110, 113, 114, 116,
                 125, 128, 132, 139, 140, 144, 148, 149, 151, 161,
                 162, 167, 171, 173, 174, 177, 179, 181, 182, 186,
                 187, 188, 189, 191, 192, 195, 197, 202, 205, 207]

  if verbose: print("Adding clients...")
  groups = [group_world, group_dev, group_eval]
  lists  = [list_world, list_dev, list_eval]
  for k in range(len(groups)):
    g_cur = groups[k]
    l_cur = lists[k]
    for el in l_cur:
      if verbose>1: print("  Adding client '%d'..." %(el,))
      session.add(Client(el, g_cur))

def add_files(session, imagedir, verbose):
  """Add files to the Biosecure database."""

  def add_file(session, basename, camera, verbose):
    """Parse a single filename and add it to the list.
       Also add a client entry if not already in the database."""
    v = os.path.splitext(basename)[0].split('_')
    if verbose>1: print("  Adding file '%s'..." %(basename,))
    session.add(File(int(v[0][1:4]), os.path.join(camera, basename), int(v[1][2]), camera, int(v[4])))

  for camera in filter(nodot, os.listdir(imagedir)):
    if not camera in ['ca0', 'caf', 'wc']:
      continue

    camera_dir = os.path.join(imagedir, camera)
    if verbose: print("Adding files for camera '%s'" % camera)
    for filename in filter(nodot, os.listdir(camera_dir)):
      basename, extension = os.path.splitext(filename)
      add_file(session, basename, camera, verbose)

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


def add_protocols(session, verbose):
  """Adds protocols"""

  # 1. DEFINITIONS
  # Numbers in the lists correspond to session identifiers
  protocol_definitions = {}

  # Protocol ca0
  enroll = [1, 2]
  probe = [1, 2]
  protocol_definitions['ca0'] = [enroll, probe]

  # Protocol caf
  enroll = [1, 2]
  probe = [1, 2]
  protocol_definitions['caf'] = [enroll, probe]

  # Protocol wc
  enroll = [1, 2]
  probe = [1, 2]
  protocol_definitions['wc'] = [enroll, probe]

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
      elif(key == 1 or key == 2): client_group = "dev"
      elif(key == 3 or key == 4): client_group = "eval"
      session_list = []
      if(key == 0 or key == 1 or key == 3):
        session_list = protocol_definitions[proto][0]
      elif(key == 2 or key == 4):
        session_list = protocol_definitions[proto][1]

      # Adds 'protocol' files
      for sid in session_list:
        q = session.query(File).join(Client).filter(Client.sgroup == client_group).\
              filter(and_(File.session_id == sid, File.camera == p.name)).\
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
  add_clients(s, args.verbose)
  add_files(s, args.imagedir, args.verbose)
  add_annotations(s, args.annotdir, args.verbose)
  add_protocols(s, args.verbose)
  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', help="Do SQL operations in a verbose way")
  parser.add_argument('-D', '--imagedir', metavar='DIR', default='/idiap/group/biometric/databases/biosecure/', help="Change the relative path to the directory containing the images of the Biosecure database.")
  parser.add_argument('-A', '--annotdir', metavar='DIR', default='/idiap/group/biometric/annotations/biosecure/EyesPosition', help="Change the relative path to the directory containing the annotations of the BANCA database (defaults to %(default)s)")

  parser.set_defaults(func=create) #action
