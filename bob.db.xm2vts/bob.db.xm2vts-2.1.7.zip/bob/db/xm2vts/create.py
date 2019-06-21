#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Wed 6 Jul 20:58:23 2011
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

"""This script creates the XM2VTS database in a single pass.
"""

import os

from .models import *

def nodot(item):
  """Can be used to ignore hidden files, starting with the . character."""
  return item[0] != '.'

def add_clients(session, verbose):
  """Add clients to the XM2VTS database."""
  # clients
  client_list = [  3,   4,   5,   6,   9,  12,  13,  16,  17,  18,
                  19,  20,  21,  22,  24,  25,  26,  27,  29,  30,
                  32,  33,  34,  35,  36,  37,  38,  40,  41,  42,
                  45,  47,  49,  50,  51,  52,  53,  54,  55,  56,
                  58,  60,  61,  64,  65,  66,  68,  69,  71,  72,
                  73,  74,  75,  78,  79,  80,  82,  85,  89,  90,
                  91,  92,  99, 101, 102, 103, 105, 108, 110, 112,
                 113, 115, 116, 121, 122, 123, 124, 125, 126, 129,
                 132, 133, 135, 136, 137, 138, 140, 141, 145, 146,
                 148, 150, 152, 154, 159, 163, 164, 165, 166, 167,
                 168, 169, 173, 178, 179, 180, 181, 182, 183, 188,
                 191, 193, 196, 197, 198, 206, 207, 208, 209, 210,
                 211, 213, 216, 218, 219, 221, 222, 224, 227, 228,
                 229, 231, 232, 233, 235, 236, 237, 240, 243, 244,
                 246, 248, 249, 253, 255, 258, 259, 261, 264, 266,
                 267, 269, 270, 274, 275, 278, 279, 281, 282, 285,
                 287, 288, 289, 290, 292, 293, 295, 305, 310, 312,
                 316, 319, 320, 321, 322, 324, 325, 328, 329, 330,
                 332, 333, 334, 336, 337, 338, 339, 340, 342, 357,
                 358, 359, 360, 362, 364, 365, 366, 369, 370, 371]
  if verbose: print("Adding clients...")
  for cid in client_list:
    if verbose>1: print("  Adding client '%d' on 'client' group..." % (cid))
    session.add(Client(cid, 'client'))
  # impostorDev
  impostorDev_list = [  0,   2,   7,  46,  57,  62,  83,  93, 104, 120,
                      143, 157, 158, 177, 187, 189, 203, 212, 215, 242,
                      276, 284, 301, 314, 331]
  for cid in impostorDev_list:
    if verbose>1: print("  Adding client '%d' on 'impostorDev' group..." % (cid))
    session.add(Client(cid, 'impostorDev'))
  # impostorEval
  impostorEval_list = [  1,   8,  10,  11,  23,  28,  31,  39,  43,  44,
                        48,  59,  67,  70,  81,  86,  87,  88,  95,  96,
                        98, 107, 109, 111, 114, 119, 127, 128, 130, 131,
                       134, 142, 147, 149, 153, 155, 160, 161, 170, 171,
                       172, 174, 175, 176, 185, 190, 199, 200, 201, 202,
                       225, 226, 234, 241, 250, 263, 271, 272, 280, 283,
                       286, 300, 313, 315, 317, 318, 323, 335, 341, 367]
  for cid in impostorEval_list:
    if verbose>1 : print("  Adding client '%d' on 'impostorEval' group..." % (cid))
    session.add(Client(cid, 'impostorEval'))

def add_files(session, imagedir, verbose):
  """Add files to the XM2VTS database."""

  def add_file(session, basename, client_dir, subdir):
    """Parse a single filename and add it to the list."""
    v = os.path.splitext(basename)[0].split('_')
    if(subdir == 'frontal'):
      session.add(File(int(v[0]), os.path.join(subdir, client_dir, basename), int(v[1]), 'n', int(v[2])))
    elif(subdir == 'darkened'):
      session.add(File(int(v[0]), os.path.join(subdir, client_dir, basename), 4, v[2][0], int(v[2][1])))

  for subdir in ('frontal', 'darkened'):
    if verbose: print("Adding files of sub-dir '%s'..." % subdir)
    imagedir_app = os.path.join(imagedir,subdir)
    file_list = os.listdir(imagedir_app)
    for cl_dir in filter(nodot, file_list):
      if os.path.isdir(os.path.join(imagedir_app, cl_dir)):
        client_dir = os.path.join(imagedir_app, cl_dir)
        for filename in filter(nodot, os.listdir(client_dir)):
          basename, extension = os.path.splitext(filename)
          if verbose>1: print("  Adding file '%s'..." % (basename))
          add_file(session, basename, cl_dir, subdir)

def add_annotations(session, annotdir, verbose, only_filename = False):
  """Reads annotation files of the XM2VTS database and stores the annotations in the sql database."""

  def read_annotation(filename, file_id):
    # read the eye positions, which are stored as four integers in one line
    line = open(filename, 'r').readline()
    positions = line.split()
    assert len(positions) == 4
    return Annotation(file_id, positions)

  # iterate though all stored images and try to access the annotations
  session.flush()
  if verbose: print("Adding annotations from directory '%s' ..."%annotdir)
  files = session.query(File)
  for f in files:
    if only_filename:
      annot_file = os.path.join(annotdir, os.path.basename(f.path) + '.pos')
    else:
      annot_file = f.make_path(annotdir, '.pos')
    if os.path.exists(annot_file):
      if verbose>1: print("  Adding annotation '%s'..." %(annot_file, ))
      session.add(read_annotation(annot_file, f.id))


def add_protocols(session, verbose):
  """Adds protocols"""

  # 1. DEFINITIONS
  protocol_definitions = {}
  all_normal = [(1, 'n', 1), (1, 'n', 2), (2, 'n', 1), (2, 'n', 2), (3, 'n', 1), (3, 'n', 2), (4, 'n', 1), (4, 'n', 2)]
  all_darkened = [(4, 'l', 1), (4, 'l', 2), (4, 'r', 1), (4, 'r', 2)]
  # Protocol lp1
  enroll = [(1, 'n', 1), (2, 'n', 1), (3, 'n', 1)]
  dev_probe_c = [(1, 'n', 2), (2, 'n', 2), (3, 'n', 2)]
  dev_probe_i = all_normal
  eval_probe_c = [(4, 'n', 1), (4, 'n', 2)]
  eval_probe_i = all_normal
  protocol_definitions['lp1'] = [enroll, dev_probe_c, dev_probe_i, eval_probe_c, eval_probe_i]

  # Protocol lp2
  enroll = [(1, 'n', 1), (1, 'n', 2), (2, 'n', 1), (2, 'n', 2)]
  dev_probe_c = [(3, 'n', 1), (3, 'n', 2)]
  dev_probe_i = all_normal
  eval_probe_c = [(4, 'n', 1), (4, 'n', 2)]
  eval_probe_i = all_normal
  protocol_definitions['lp2'] = [enroll, dev_probe_c, dev_probe_i, eval_probe_c, eval_probe_i]

   # Protocol darkened-lp1
  enroll = [(1, 'n', 1), (2, 'n', 1), (3, 'n', 1)]
  dev_probe_c = [(1, 'n', 2), (2, 'n', 2), (3, 'n', 2)]
  dev_probe_i = all_normal
  eval_probe_c = [(4, 'l', 1), (4, 'l', 2), (4, 'r', 1), (4, 'r', 2)]
  eval_probe_i = all_darkened
  protocol_definitions['darkened-lp1'] = [enroll, dev_probe_c, dev_probe_i, eval_probe_c, eval_probe_i]

   # Protocol darkened-lp2
  enroll = [(1, 'n', 1), (1, 'n', 2), (2, 'n', 1), (2, 'n', 2)]
  dev_probe_c = [(3, 'n', 1), (3, 'n', 2)]
  dev_probe_i = all_normal
  eval_probe_c = [(4, 'l', 1), (4, 'l', 2), (4, 'r', 1), (4, 'r', 2)]
  eval_probe_i = all_darkened
  protocol_definitions['darkened-lp2'] = [enroll, dev_probe_c, dev_probe_i, eval_probe_c, eval_probe_i]

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
      list_properties = []
      list_properties_i = []
      impostor_val = ''
      if(key == 0 or key == 1 or key == 3): # world/enroll data
        list_properties = protocol_definitions[proto][0]
      elif(key == 2):
        list_properties = protocol_definitions[proto][1]
        list_properties_i = protocol_definitions[proto][2]
        impostor_val = 'impostorDev'
      elif(key == 4):
        list_properties = protocol_definitions[proto][3]
        list_properties_i = protocol_definitions[proto][4]
        impostor_val = 'impostorEval'

      # Loops over the properties list which defines the protocol
      for el in list_properties:
        q = session.query(File).join(Client).\
              filter(Client.sgroup == 'client').\
              filter(and_(File.session_id == el[0], File.darkened == el[1], File.shot_id == el[2])).\
              order_by(File.id)
        for k in q:
          if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
          pu.files.append(k)

      # Adds impostors if required
      if(key == 2 or key == 4):
        for el in list_properties_i:
          q = session.query(File).join(Client).\
                filter(Client.sgroup == impostor_val).\
                filter(and_(File.session_id == el[0], File.darkened == el[1], File.shot_id == el[2])).\
                order_by(File.id)
          for k in q:
            if verbose>1: print("    Adding protocol file (impostor) '%s'..." % (k.path))
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
  if args.annotsub:
    for subdir in args.annotsub:
      add_annotations(s, os.path.join(args.annotdir, subdir), args.verbose, True)
  else:
    add_annotations(s, args.annotdir, args.verbose)
  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', help="Do SQL operations in a verbose way?")
  parser.add_argument('-D', '--imagedir', metavar='DIR', default='/idiap/resource/database/xm2vtsdb/images/', help="Change the relative path to the directory containing the images of the XM2VTS database.")
  parser.add_argument('-A', '--annotdir', metavar='DIR', default='/idiap/group/biometric/annotations/xm2vts/', help="Change the relative path to the directory containing the annotations of the XM2VTS database (defaults to %(default)s)")
  parser.add_argument('-S', '--annotsub', metavar='DIR', nargs='+', help="Sub-directories of the XM2VTS annotation directory to consider, which will replace the stem path of the registered Files")

  parser.set_defaults(func=create) #action
