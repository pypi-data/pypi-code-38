#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Mon Dec 10 14:29:51 CET 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This script creates the CAS-PEAL database in a single pass.
"""

from __future__ import print_function

import os

from .models import *


def read_all_eyes(directory, sub_dirs = ('FRONTAL', 'POSE')):
  """Scans the image directories for files containing the hand-labeled eye positions, reads them and stores everything in one huge dictionary"""
  # scan for the directories, where we expect images
  all_sub_dirs = [[sub_dir, s] for sub_dir in sub_dirs for s in os.listdir(os.path.join(directory, sub_dir)) if os.path.isdir(os.path.join(directory, sub_dir, s))]

  # read eye positions
  eyes = {}
  for sub_dirs in all_sub_dirs:
    # eye position file
    eyes_file = os.path.join(directory, *(sub_dirs + ["FaceFP_2.txt"]))
    with open(eyes_file) as f:
      for line in f:
        # get the information
        splits = line.rstrip().split()
        # add the eyes positions, by generating keys according to the default names in the CAS-PEAL file lists
        eyes["\\".join(sub_dirs + splits[:1])] = [int(p) for p in splits[1:]]
  return eyes

def add_all_elements(session, directory, extension, add_pose, verbose):
  """Adds the clients, the files and the protocols of the CAS-PEAL database."""
  list_files = {
      'training'  : os.path.join(directory, "Evaluation Prototype", "Training Set", "Training Set.txt"),
      'gallery'   : os.path.join(directory, "Evaluation Prototype", "Gallery", "Gallery.txt"),
      'accessory' : os.path.join(directory, "Evaluation Prototype", "Probe Sets", "Probe Set_Accessory.txt"),
      'aging'     : os.path.join(directory, "Evaluation Prototype", "Probe Sets", "Probe Set_Aging.txt"),
      'background': os.path.join(directory, "Evaluation Prototype", "Probe Sets", "Probe Set_Background.txt"),
      'distance'  : os.path.join(directory, "Evaluation Prototype", "Probe Sets", "Probe Set_Distance.txt"),
      'expression': os.path.join(directory, "Evaluation Prototype", "Probe Sets", "Probe Set_Expression.txt"),
      'lighting'  : os.path.join(directory, "Evaluation Prototype", "Probe Sets", "Probe Set_Lighting.txt"),
      # The pose probe set is handled a bit different, see also note below
      #'pose'      : os.path.join(directory, "Evaluation Prototype", "Probe Sets", "Probe Set_Pose.txt"),
  }

  # create clients (all clients are enrolled, i.e., contained in the gallery list)
  with open(list_files['gallery']) as f:
    if verbose: print("Adding clients ...")
    for line in f:
      splits = line.split("\\")[-1].split("_")
      if verbose>1: print("  Adding client '%s'" % Client(splits[0], splits[1]).id)
      session.add(Client(splits[0], splits[1]))

  # create files and protocols
  eyes = read_all_eyes(directory)
  for protocol in list_files:
    if verbose: print("Adding protocol '%s'" % protocol)
    # create protocol
    p = Protocol(protocol)
    # add it to the session and make it get an id
    session.add(p)
    session.flush()
    session.refresh(p)
    # read file list and add files
    with open(list_files[protocol]) as f:
      for line in f:
        file = File(line.strip(), p)
        if verbose>1: print("  Adding file '%s'" % file.path, end=' ')
        # make the file get an id
        session.add(file)
        session.flush()
        session.refresh(file)
        # add annotations for the file
        if verbose>1: print("with annotations '%s'" % eyes[line.strip()])
        session.add(Annotation(file.id, eyes[line.strip()]))

  # create pose protocol
  # Note: I am not sure if this is really useful.
  # pose images are not listed, but instead we use all pose images
  # THIS ALSO MEANS, THERE IS NO TRAINING IMAGES FOR POSE!
  # additionally, the poses differ between subjects: most have a poses (0, +-15, +-30, +-45), but some have (0, +-22, +-45, +-66)
  if add_pose:
    p = Protocol('pose')
    if verbose: print("Adding 'pose' protocol")
    # add it to the session and make it get an id
    session.add(p)
    session.flush()
    session.refresh(p)
    # get directories
    pose_sub_dirs = [['POSE', s] for s in os.listdir(os.path.join(directory, 'POSE')) if os.path.isdir(os.path.join(directory, 'POSE', s))]
    for sub_dirs in pose_sub_dirs:
      sub_dir = os.path.join(directory, *sub_dirs)
      files = [f for f in os.listdir(sub_dir) if os.path.isfile(os.path.join(sub_dir,f)) and os.path.splitext(f)[1] == extension]
      for f in files:
        file_in_dir = "\\".join(sub_dirs + [os.path.splitext(f)[0]])
        file = File(file_in_dir, p)
        if verbose>1: print("  Adding file '%s'" % file.path, end=' ')
        session.add(file)
        session.flush()
        session.refresh(file)
        if verbose>1: print("with annotations '%s'" % eyes[file_in_dir])
        session.add(Annotation(file.id, eyes[file_in_dir]))


def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
  Client.metadata.create_all(engine)
  File.metadata.create_all(engine)
  Protocol.metadata.create_all(engine)


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
  add_all_elements(s, args.directory, args.extension, args.poses, args.verbose)
  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help='If set, I\'ll first erase the current database')
  parser.add_argument('-v', '--verbose', action='count', help='Do SQL operations in a verbose way?')
  parser.add_argument('-p', '--poses', action='store_true', help='Shall the pose files also be added?')
  parser.add_argument('-D', '--directory', metavar='DIR', default='/idiap/resource/database/CAS-PEAL', help='The path to the CAS-PEAL database')
  parser.add_argument('--extension', metavar='STR', default='.tif', help='The file extension of the image files from the CAS-PEAL face database')

  parser.set_defaults(func=create) #action
