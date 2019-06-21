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

"""This script creates the SCFace database in a single pass.
"""

import os

from .models import *

def nodot(item):
  """Can be used to ignore hidden files, starting with the . character."""
  return item[0] != '.'

def add_clients(session, filename, verbose):
  """Add clients to the SCFace database."""

  if verbose: print("Adding clients...")
  # open features.txt file containing information about the clients
  f = open(filename, 'r')
  c = 0
  for line in f:
    # Ignore the 10 first (useless) lines
    c = c + 1
    if c<=10:
      continue

    # parse the line
    tok = line.split('\t')

    # birthyear
    birthyear = tok[1].split('.')[2]
    # group
    if int(tok[0]) <= 43:
      group = 'world'
    elif int(tok[0]) <= 87:
      group = 'dev'
    else:
      group = 'eval'
    # gender
    if int(tok[2]) == 0:
      gender = 'm'
    else:
      gender = 'f'

    # Add the client
    if verbose>1: print("  Adding client '%s'..." %tok[0])
    session.add(Client(int(tok[0]), group, int(birthyear), gender, int(tok[3]), int(tok[4]), int(tok[5])))

def add_subworlds(session, verbose):
  """Adds splits in the world set, based on the client ids"""
  # one third
  snames = ['onethird', 'twothirds']
  slists = [[ 1,  4,  5,  6,  8, 11, 12, 18, 20, 30,
             33, 36, 39, 40],
            [ 2,  3,  7,  9, 10, 13, 14, 15, 16, 17,
             19, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             31, 32, 34, 35, 37, 38, 41, 42, 43]]
  for k in range(len(snames)):
    if verbose: print("Adding subworld '%s'" %(snames[k], ))
    su = Subworld(snames[k])
    session.add(su)
    session.flush()
    session.refresh(su)
    l = slists[k]
    for c_id in l:
      if verbose>1: print("  Adding client '%d' to subworld '%s'..." %(c_id, snames[k]))
      su.clients.append(session.query(Client).filter(Client.id == c_id).first())

def add_files(session, imagedir, verbose):
  """Add files to the SCFace database."""

  def add_file(session, basename, maindir, frontal, verbose):
    """Parse a single filename and add it to the list."""
    v = os.path.splitext(basename)[0].split('_')
    if verbose>1: print("  Adding file '%s'..." %(basename, ))
    if frontal:
      session.add(File(int(v[0]), os.path.join(maindir, basename), 'frontal', 0))
    else:
      if len(v) == 2:
        session.add(File(int(v[0]), os.path.join(maindir, basename), v[1], 0))
      else:
        session.add(File(int(v[0]), os.path.join(maindir, basename), v[1], int(v[2])))

  for maindir in ['mugshot_frontal_cropped_all', 'surveillance_cameras_distance_1',\
                  'surveillance_cameras_distance_2', 'surveillance_cameras_distance_3',
                  'surveillance_cameras_IR_cam8']:
    if verbose: print("Adding files from dir '%s'" % maindir)
    if not os.path.isdir( os.path.join( imagedir, maindir) ):
      continue
    elif maindir in ('mugshot_frontal_cropped_all', 'surveillance_cameras_IR_cam8'):
      for f in filter(nodot, os.listdir( os.path.join( imagedir, maindir) )):
        basename, extension = os.path.splitext(f)
        add_file(session, basename, maindir, maindir=='mugshot_frontal_cropped_all', verbose)
    else:
      for camdir in filter(nodot, os.listdir( os.path.join( imagedir, maindir) )):
        subdir = os.path.join(maindir, camdir)
        for f in filter(nodot, os.listdir( os.path.join( imagedir, subdir) )):
          basename, extension = os.path.splitext(f)
          add_file(session, basename, subdir, False, verbose)


def add_annotations(session, annotation_file, verbose):
  """Reads the annotation file and adds the annotations to the .sql3 database."""

  # iterate though all stored images and try to access the annotations
  session.flush()
  if verbose: print("Reading annotations file '%s' ..." % annotation_file)
  annotations = {}
  # read the annotation file
  with open(annotation_file, 'r') as f:
    for line in f:
      line = line.rstrip()
      # skip empty and comment lines
      if line and line[0] != '#':
        splits = line.split()
        # check validity
        assert len(splits) == 9
        assert splits[0] not in annotations
        # add annotations
        annotations[splits[0]] = splits[1:]

  if verbose: print("Adding annotations ...")
  files = session.query(File)
  for f in files:
    # get the filename w/o extension
    filename = os.path.basename(f.path)
    if filename in annotations:
      if verbose>1: print("  Adding annotation '%s'..." %(filename, ))
      session.add(Annotation(f.id, annotations[filename]))
    else:
      print("Could not read annotations for file '%s'" % filename)


def add_protocols(session, verbose):
  """Adds protocols"""

  # 1. DEFINITIONS
  # Numbers in the lists correspond to session identifiers
  protocol_definitions = {}

  # Protocol combined
  world = [(['frontal', 'cam1', 'cam2', 'cam3', 'cam4', 'cam5',], [])]
  enroll = [(['frontal'], [0])]
  probe = [(['cam1', 'cam2', 'cam3', 'cam4', 'cam5'], [1,2,3])]
  protocol_definitions['combined'] = [world, enroll, probe]

  # Protocol close
  world = [(['frontal', 'cam1', 'cam2', 'cam3', 'cam4', 'cam5'], [])]
  enroll = [(['frontal'], [0])]
  probe = [(['cam1', 'cam2', 'cam3', 'cam4', 'cam5'], [3])]
  protocol_definitions['close'] = [world, enroll, probe]

  # Protocol medium
  world = [(['frontal', 'cam1', 'cam2', 'cam3', 'cam4', 'cam5'], [])]
  enroll = [(['frontal'], [0])]
  probe = [(['cam1', 'cam2', 'cam3', 'cam4', 'cam5'], [2])]
  protocol_definitions['medium'] = [world, enroll, probe]

  # Protocol far
  world = [(['frontal', 'cam1', 'cam2', 'cam3', 'cam4', 'cam5'], [])]
  enroll = [(['frontal'], [0])]
  probe = [(['cam1', 'cam2', 'cam3', 'cam4', 'cam5'], [1])]
  protocol_definitions['far'] = [world, enroll, probe]

  # Protocol IR
  world = [(['cam6', 'cam7', 'cam8'], [])]
  enroll = [(['cam8'], [0])]
  probe = [(['cma6', 'cam7'], [1])]
  protocol_definitions['IR'] = [world, enroll, probe]


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
      prop_list = []
      if(key == 0): client_group = "world"
      elif(key == 1 or key == 2): client_group = "dev"
      elif(key == 3 or key == 4): client_group = "eval"
      if(key == 0):
        prop_list = protocol_definitions[proto][0]
      if(key == 1 or key == 3):
        prop_list = protocol_definitions[proto][1]
      elif(key == 2 or key == 4):
        prop_list = protocol_definitions[proto][2]

      # Adds 'protocol' files
      for el in prop_list:
        cams = el[0] # list of camera identifiers
        dids = el[1] # list of distance identifiers
        q = session.query(File).join(Client).\
              filter(Client.sgroup == client_group)
        if cams:
          q = q.filter(File.camera.in_(cams))
        if dids:
          q = q.filter(File.distance.in_(dids))
        q = q.order_by(File.id)
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
  add_clients(s, args.featuresfile, args.verbose)
  add_subworlds(s, args.verbose)
  add_files(s, args.imagedir, args.verbose)
  add_protocols(s, args.verbose)
  add_annotations(s, args.annotfile, args.verbose)
  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', help="Do SQL operations in a verbose way")
  parser.add_argument('--featuresfile', metavar='FILE', default='/idiap/resource/database/scface/SCface_database/features.txt', help="Change the path to the file containing information about the clients of the SCFace database.")
  parser.add_argument('-D', '--imagedir', metavar='DIR', default='/idiap/group/biometric/databases/scface/images', help="Change the relative path to the directory containing the images of the SCFace database.")
  import pkg_resources
  parser.add_argument('-A', '--annotfile', metavar='DIR', default=pkg_resources.resource_filename(__name__, 'scface_annotations.txt'), help="Change the relative path to the directory containing the images of the SCFace database.")

  parser.set_defaults(func=create) #action
