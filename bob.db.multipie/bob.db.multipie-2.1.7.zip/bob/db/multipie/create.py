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

"""This script creates the Multi-PIE database in a single pass.
"""

import os
import fileinput

from .models import *

def nodot(item):
  """Can be used to ignore hidden files, starting with the . character."""
  return item[0] != '.'

def add_clients(session, filelist, verbose):
  """Add files (and clients) to the Multi-PIE database."""

  # Define development and evaluation set in term of client ids
  dev_ids =   [2, 4, 6, 8, 10, 15, 18, 20, 22, 27, 33, 35, 38, 40, 42, 46, 48, 50, 52, 54, 57, 64, 68, 69, 71, 78, 80, 85, 97, 102,
              105, 107, 110, 111, 115, 118, 123, 125, 126, 128, 132, 137, 139, 143, 149, 157, 167, 169, 170, 177, 184, 186, 190, 191,
              193, 198, 202, 205, 208, 220, 227, 235, 241, 248]

  eval_ids =  [3, 5, 9, 11, 14, 17, 19, 23, 28, 29, 34, 36, 41, 43, 44, 47, 49, 53, 55, 56, 62, 67, 70, 74, 76, 79, 83, 100, 103, 104,
              106, 108, 112, 116, 117, 122, 124, 127, 129, 131, 133, 138, 145, 150, 156, 161, 168, 175, 178, 181, 185, 188, 192, 194,
              196, 199, 203, 209, 223, 225, 230, 236, 240, 246, 250]

  def add_client(session, client_string, client_dict, verbose):
    """Parse a single client string and add its content to the database.
       Also add a client entry if not already in the database."""

    v = client_string.split(' ')
    if (v[2] == 'Male'):
      v[2] = 'male'
    elif (v[2] == 'Female'):
      v[2] = 'female'
    v[6] = v[6].rstrip() # chomp new line
    first_session = 0
    second_session = 0
    third_session = 0
    fourth_session = 0
    if(v[3] == '1'):
      first_session = 1
      if(v[4] == '1'):
        second_session = 2
        if(v[5] == '1'):
          third_session = 3
          if(v[6] == '1'):
            fourth_session = 4
        elif(v[6] == '1'):
          third_session = 4
      elif(v[5] == '1'):
        second_session = 3
        if(v[6] == '1'):
          third_session = 4
      elif(v[6] == '1'):
        second_session = 4
    elif(v[4] == '1'):
      first_session = 2
      if(v[5] == '1'):
        second_session = 3
        if(v[6] == '1'):
          third_session = 4
      elif(v[6] == '1'):
        second_session = 4
    elif(v[5] == '1'):
      first_session = 3
      if(v[6] == '1'):
        second_session = 4
    elif(v[6] == '1'):
      first_session = 4
    #TODO: if first_session == 0: raises an error

    if not (v[0] in client_dict):
      group = 'world'
      if int(v[0]) in dev_ids: group = 'dev'
      elif int(v[0]) in eval_ids: group = 'eval'
      if verbose>1: print("Adding client '%d' ..." % int(v[0]))
      session.add(Client(int(v[0]), group, int(v[1]), v[2], first_session, second_session, third_session, fourth_session))
      client_dict[v[0]] = True

  client_dict = {}
  for line in fileinput.input(filelist):
    add_client(session, line, client_dict, verbose)

def add_subworlds(session, verbose):
  """Adds splits in the world set, based on the client ids"""

  # Lists for the subworld subsets
  l41 =  [ 21,  26,  31,  39,  66,  75,  81,  90,  98, 109, 114, 148, 152, 158, 165, 171, 174, 179, 182, 197,
          207, 215, 226, 239, 244, 256, 271, 277, 303, 309, 310, 315, 321, 326, 327, 333, 336, 338, 339, 341,
          342]
  l81 =  [ 16,  21,  26,  31,  37,  39,  51,  65,  66,  73,  75,  81,  84,  86,  87,  90,  94,  95,  98,  99,
          109, 114, 134, 142, 144, 148, 151, 152, 158, 164, 165, 171, 173, 174, 179, 182, 195, 197, 207, 215,
          217, 222, 226, 239, 244, 247, 249, 251, 256, 259, 260, 263, 264, 265, 271, 272, 276, 277, 287, 298,
          303, 304, 306, 309, 310, 312, 315, 317, 319, 320, 321, 324, 326, 327, 329, 333, 336, 338, 339, 341,
          342]
  l121 = [  7,  16,  21,  24,  26,  30,  31,  37,  39,  51,  60,  61,  63,  65,  66,  72,  73,  75,  81,  84,
           86,  87,  90,  91,  94,  95,  96,  98,  99, 109, 114, 134, 135, 142, 144, 148, 151, 152, 158, 159,
          164, 165, 166, 171, 173, 174, 176, 179, 180, 182, 195, 197, 207, 210, 214, 215, 217, 221, 222, 226,
          228, 231, 233, 234, 239, 242, 244, 247, 249, 251, 253, 254, 255, 256, 259, 260, 263, 264, 265, 268,
          271, 272, 276, 277, 278, 279, 285, 287, 291, 292, 293, 294, 297, 298, 300, 301, 303, 304, 306, 309,
          310, 311, 312, 315, 317, 319, 320, 321, 322, 324, 325, 326, 327, 329, 333, 336, 338, 339, 341, 342,
          344]
  l161 = [  7,  12,  13,  16,  21,  24,  26,  30,  31,  37,  39,  45,  51,  60,  61,  63,  65,  66,  72,  73,
           75,  77,  81,  82,  84,  86,  87,  88,  90,  91,  93,  94,  95,  96,  98,  99, 101, 109, 114, 119,
          120, 121, 134, 135, 136, 142, 144, 148, 151, 152, 153, 158, 159, 160, 162, 163, 164, 165, 166, 171,
          173, 174, 176, 179, 180, 182, 187, 195, 197, 200, 207, 210, 214, 215, 216, 217, 218, 219, 221, 222,
          226, 228, 229, 231, 233, 234, 237, 239, 242, 244, 247, 249, 251, 253, 254, 255, 256, 257, 259, 260,
          261, 263, 264, 265, 267, 268, 271, 272, 273, 276, 277, 278, 279, 285, 287, 289, 291, 292, 293, 294,
          295, 296, 297, 298, 299, 300, 301, 303, 304, 306, 308, 309, 310, 311, 312, 313, 314, 315, 317, 319,
          320, 321, 322, 323, 324, 325, 326, 327, 329, 333, 335, 336, 337, 338, 339, 341, 342, 343, 344, 345,
          346]
  snames = ['sub41', 'sub81', 'sub121', 'sub161']
  slist = [l41, l81, l121, l161]
  for k in range(len(snames)):
    if verbose: print("Adding subworld '%s'" %(snames[k], ))
    su = Subworld(snames[k])
    session.add(su)
    session.flush()
    session.refresh(su)
    l = slist[k]
    for c_id in l:
      if verbose>1: print("Adding client '%d' to subworld '%s'..." %(c_id, snames[k]))
      su.clients.append(session.query(Client).filter(Client.id == c_id).first())

def add_files(session, imagedir, illuminations, poses, expressions, highresolutions, verbose):
  """Add files (and clients) to the Multi-PIE database."""

  def add_mv_file(session, filename, session_id, client_id, recording_id, camera_name, expr_dict, cam_dict, expressions, verbose):
    """Parse a single filename and add it to the list.
       Also add a client entry if not already in the database."""
    v = os.path.splitext(filename)[0].split('_')
    shot_id = int(v[5])
    if illuminations or shot_id == 0:
      if verbose>1: print("Adding file (multiview) '%s' ..." %(filename,))
      sid = int(session_id[8])
      rid = int(recording_id)
      eid = expr_dict[(sid,rid)][0]
      ename = expr_dict[(sid,rid)][1]
      cid = cam_dict[camera_name]
      if (expressions == True or ename == 'neutral'):
        f = File(int(client_id), filename, sid, rid, 'multiview', eid)
        # We want to make use of the new assigned file id
        # We need to do the following:
        session.add(f)
        session.flush()
        session.refresh(f)
        session.add(FileMultiview(f.id, shot_id, cid))

  def add_hr_file(session, filename, session_id, client_id, expr_dict, expressions, verbose):
    """Parse a single filename and add it to the list.
       Also add a client entry if not already in the database."""
    if verbose>1: print("Adding file (highres) '%s' ..." %(filename,))
    v = os.path.splitext(filename)[0].split('_')
    sid = int(session_id[8])
    rid = int(v[1])
    eid = expr_dict[(sid,rid)][0]
    ename = expr_dict[(sid,rid)][1]
    if (expressions == True or ename == 'neutral'):
      session.add(File(int(client_id), filename, sid, rid, 'highres', eid))

  def add_expressions(session, verbose):
    """Adds expressions"""

    expr_list = ['neutral', 'smile', 'surprise', 'squint', 'disgust', 'scream']
    expr_srid = [[(1,1), (2,1), (3,1), (4,1), (4,2)], [(1,2), (3,2)], [(2,2)], [(2,3)], [(3,3)], [(4,3)]]
    expr_dict = {}
    for k in range(len(expr_list)):
      el = expr_list[k]
      if verbose: print("Adding expression '%s'..." % (el))
      e = Expression(el)
      session.add(e)
      session.flush()
      session.refresh(e)
      indices = expr_srid[k]
      for ind in indices:
        expr_dict[ind] = [e.id, e.name]
    return expr_dict

  def add_cameras(session, verbose):
    """Adds cameras"""

    cam_list = ['24_0', '01_0', '20_0', '19_0', '04_1', '19_1', '05_0', '05_1', '14_0', '08_1',
                '13_0', '08_0', '09_0', '12_0', '11_0']
    cam_dict = {}
    for el in cam_list:
      if verbose: print("Adding cameras '%s'..." % (el))
      c = Camera(el)
      session.add(c)
      session.flush()
      session.refresh(c)
      cam_dict[el] = c.id
    return cam_dict

  # Start by creating the expressions and the cameras
  expr_dict = add_expressions(session, verbose)
  cam_dict = add_cameras(session, verbose)

  # session
  for session_id in filter(nodot, os.listdir(imagedir)):
    if verbose: print("Adding files for session '%s'..." % (session_id))
    se_dir = os.path.join(imagedir, session_id)

    # multiview
    mv_dir = os.path.join(se_dir, 'multiview')
    # client id
    for client_id in filter(nodot, os.listdir(mv_dir)):
      client_dir = os.path.join(mv_dir, client_id)
      # recording id
      for recording_id in filter(nodot, os.listdir(client_dir)):
        recording_dir = os.path.join(client_dir, recording_id)
        # camera name
        for camera_name in filter(nodot, os.listdir(recording_dir)):
          # Check if it is the frontal camera 05_1
          if ((not poses) and camera_name != '05_1'):
            continue
          camera_dir = os.path.join(recording_dir, camera_name)
          # flashes/images
          for filename in filter(nodot, os.listdir(camera_dir)):
            basename, extension = os.path.splitext(filename)
            add_mv_file(session, os.path.join( session_id, 'multiview', client_id, recording_id, camera_name, basename), session_id, client_id,
                        recording_id, camera_name, expr_dict, cam_dict, expressions, verbose)

    if highresolutions:
      # highres
      hr_dir = os.path.join(se_dir, 'highres')
      # client id
      for client_id in filter(nodot, os.listdir(hr_dir)):
        client_dir = os.path.join(hr_dir, client_id)
        # flashes/images
        for filename in filter(nodot, os.listdir(client_dir)):
          basename, extension = os.path.splitext(filename)
          add_hr_file(session, os.path.join( session_id, 'highres', client_id, basename), session_id, client_id, expr_dict, expressions, verbose)

def add_protocols(session, illuminations, poses, expressions, highresolutions, verbose):
  """Adds protocols"""

  # 1. DEFINITIONS
  # Tuples in the lists correspond to (session_ids, recording_ids, cameras, shot_ids),
  # [] value indicates all sessions/recordings/cameras/shots.
  protocol_definitions = {}

  # useful cameras and shots
  shot0 = [0]
  shots = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
  cam240 = ['24_0']
  cam010 = ['01_0']
  cam200 = ['20_0']
  cam190 = ['19_0']
  cam041 = ['04_1']
  cam191 = ['19_1']
  cam050 = ['05_0']
  cam051 = ['05_1']
  cam140 = ['14_0']
  cam081 = ['08_1']
  cam130 = ['13_0']
  cam080 = ['08_0']
  cam090 = ['09_0']
  cam120 = ['12_0']
  cam110 = ['11_0']
  cams_all = ['24_0', '01_0', '20_0', '19_0', '04_1', '19_1', '05_0', '05_1', '14_0',
              '08_1', '13_0', '08_0', '09_0', '12_0', '11_0']

  # for P protocol, we use all cameras that have the same elevation angle
  cams_all_P =['24_0', '01_0', '20_0', '19_0', '04_1', '05_0', '05_1', '14_0', '13_0', '08_0', '09_0', '12_0', '11_0']

  # ILLUMINATION (FRONTAL) PROTOCOLS
  # Protocol M: enroll: No flash; Probe: No flash
  if illuminations:
    world = [([1,2,3,4], [1], cam051, shots), ([4], [2], cam051, shots)]
    enroll = [([1], [1], cam051, shot0)]
    probe = [([2,3,4], [1], cam051, shot0), ([4], [2], cam051, shot0)]
    protocol_definitions['M'] = [world, enroll, probe]

    # Protocol U: enroll: No flash; Probe: No flash + Any flash
    world = [([1,2,3,4], [1], cam051, shots), ([4], [2], cam051, shots)]
    enroll = [([1], [1], cam051, shot0)]
    probe = [([2,3,4], [1], cam051, shots), ([4], [2], cam051, shots)]
    protocol_definitions['U'] = [world, enroll, probe]

    # Protocol G: enroll: No flash + Any flash; Probe: No flash + Any flash
    world = [([1,2,3,4], [1], cam051, shots), ([4], [2], cam051, shots)]
    enroll = [([1], [1], cam051, shots)]
    probe = [([2,3,4], [1], cam051, shots), ([4], [2], cam051, shots)]
    protocol_definitions['G'] = [world, enroll, probe]

  # POSE PROTOCOLS
  if poses:
    # The default pose protocols
    def add_pose_protocol(name, cam):
      # For world, all cameras are used, including the ones with different elevation angle
      # (specify different world_cameras on query if you like to change this behaviour)
      world = [([1,2,3,4], [1], cams_all, shot0), ([4], [2], cams_all, shot0)]
      # enrollment is always done on the frontal camera
      enroll = [([1], [1], cam051, shot0)]
      # Probe files are specific for the given camera
      probe = [([2,3,4], [1], cam, shot0), ([4], [2], cam, shot0)]
      protocol_definitions[name] = [world, enroll, probe]

    # add a 'P' protocol that probes with all files with the same elevation angle
    add_pose_protocol('P', cams_all_P)

    add_pose_protocol('P240', cam240) # right profile
    add_pose_protocol('P010', cam010) #
    add_pose_protocol('P200', cam200) # right half-profile

    add_pose_protocol('P190', cam190) #
    add_pose_protocol('P041', cam041) # right quarter-profile
    add_pose_protocol('P050', cam050) #

    add_pose_protocol('P051', cam051) # frontal protocol; same as 'M', except for the world set

    add_pose_protocol('P140', cam140) #
    add_pose_protocol('P130', cam130) # left quarter-profile
    add_pose_protocol('P080', cam080) #

    add_pose_protocol('P090', cam090) # left half-profile
    add_pose_protocol('P120', cam120) #
    add_pose_protocol('P110', cam110) # left profile

    # Add protocols also for the remaining two cameras '19_1' and '08_1'
    add_pose_protocol('P191', cam191) # right quarter-profile from above
    add_pose_protocol('P081', cam081) # left quarter-profile from above

    # TODO: Also add one global protocol (e.g. 'P2') that takes ALL cameras into consideration, including '19_1' and '08_1'?


  # EXPRESSION PROTOCOLS; currently only one
  if expressions:
    # Protocol E: enroll: Neutral expression (1x); Probe: neutral expression (4x) and other expressions
    world = [([1], [1,2], cam051, shot0), ([2,3,4], [1,2,3], cam051, shot0)]
    enroll = [([1], [1], cam051, shot0)]
    probe = [([2,3,4], [1,2,3], cam051, shot0)]
    protocol_definitions['E'] = [world, enroll, probe]


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
      elif(key == 1 or key == 3):
        prop_list = protocol_definitions[proto][1]
      elif(key == 2 or key == 4):
        prop_list = protocol_definitions[proto][2]

      # Adds 'protocol' files
      for el in prop_list:
        sids = el[0] # list of session_ids
        rids = el[1] # list of recording_ids
        cams = el[2] # list of camera_ids
        shot_ids = el[3] # list of shot_ids
        q = session.query(File).join(Client).join(FileMultiview).\
              filter(Client.sgroup == client_group)
        if sids:
          q = q.filter(File.session_id.in_(sids))
        if rids:
          q = q.filter(File.recording_id.in_(rids))
        if cams:
          q = q.join(Camera).filter(Camera.name.in_(cams))
        if shot_ids:
          q = q.filter(FileMultiview.shot_id.in_(shot_ids))
        q = q.order_by(File.id)
        for k in q:
          if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
          pu.files.append(k)

def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2))
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
  s = session_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2))
  add_clients(s, args.subjectlist, args.verbose)
  add_subworlds(s, args.verbose)
  add_files(s, args.imagedir, not args.noilluminations, args.poses, args.expressions, args.highresolutions, args.verbose)
  add_protocols(s, not args.noilluminations, args.poses, args.expressions, args.highresolutions, args.verbose)
  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', help="Do SQL operations in a verbose way")
  parser.add_argument('-D', '--imagedir', metavar='DIR', default='/idiap/resource/database/Multi-Pie/data', help="Change the relative path to the directory containing the images of the Multi-PIE database.")
  parser.add_argument('--subjectlist', default='/idiap/resource/database/Multi-Pie/meta/subject_list.txt', help="Change the file containing the subject list of the Multi-PIE database.")
  parser.add_argument('-I', '--noilluminations', action='store_true', help='If set, it will not add the illumination files (and corresponding protocols) in the database')
  parser.add_argument('-P', '--poses', action='store_true', help='If set, it will add the pose files (and corresponding protocols) in the database')
  parser.add_argument('-E', '--expressions', action='store_true', help='If set, it will add the expression files (and corresponding protocols) in the database')
  parser.add_argument('-H', '--highresolutions', action='store_true', help='If set, it will add the high-resolution files (and corresponding protocols) in the database')

  parser.set_defaults(func=create) #action
