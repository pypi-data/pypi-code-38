#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Thu May 24 10:41:42 CEST 2012
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

"""This script creates the Labeled Faces in the Wild (LFW) database in a single pass.
"""

import os

from .models import *

def nodot(item):
  """Can be used to ignore hidden files, starting with the . character."""
  return item[0] != '.'

def add_files(session, basedir, verbose):
  """Adds files to the LFW database.
     Returns dictionaries with ids of the clients and ids of the files
     in the generated SQL tables"""

  def add_client(session, client_id):
    """Adds a client to the LFW database."""
    c = Client(client_dir)
    session.add(c)
    return c.id

  def add_file(session, file_name):
    """Parses a single filename and add it to the list."""
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    shot_id = base_name.split('_')[-1]
    client_id = base_name[0:-len(shot_id)-1]
    f = File(client_id, shot_id)
    session.add(f)

  # Loops over the directory structure
  if verbose: print("Adding clients and files ...")
  imagedir = os.path.join(basedir, 'all_images')
  for client_dir in filter(nodot, sorted([d for d in os.listdir(imagedir)])):
    # adds a client to the database
    client_name = add_client(session, client_dir)
    if verbose>1: print("  Adding client '%s'" % client_name)
    for filename in filter(nodot, sorted([d for d in os.listdir(os.path.join(imagedir, client_dir))])):
      if filename.endswith('.jpg'):
        # adds a file to the database
        if verbose>1: print("    Adding file '%s'" % filename)
        add_file(session, filename)


def add_people(session, basedir, verbose):
  """Adds the people to the LFW database"""

  def add_client(session, protocol, client_id, count):
    """Adds all images of a client"""
    for i in range(1,count+1):
      if verbose>1: print("  Adding file '%s' to protocol '%s'" % (filename(client_id, i), protocol))
      file_id = session.query(File).filter(File.name == filename(client_id, i)).first().id
      session.add(People(protocol, file_id))

  def parse_view1(session, filename, protocol):
    """Parses a file containing the people of view 1 of the LFW database"""
    pfile = open(filename)
    for line in pfile:
      llist = line.split()
      if len(llist) == 2: # one person and the number of images
        add_client(session, protocol, llist[0], int(llist[1]))

  def parse_view2(session, filename):
    """Parses the file containing the people of view 2 of the LFW database"""
    fold_id = 0
    pfile = open(filename)
    for line in pfile:
      llist = line.split()
      if len(llist) == 1: # the number of persons in the list
        protocol = "fold"+str(fold_id)
        fold_id += 1
      elif len(llist) == 2: # one person and the number of images
        add_client(session, protocol, llist[0], int(llist[1]))


  # Adds view1 people
  if verbose: print("Adding people from 'peopleDevTrain.txt' ...")
  parse_view1(session, os.path.join(basedir, 'view1', 'peopleDevTrain.txt'), 'train')
  if verbose: print("Adding people from 'peopleDevTest.txt' ...")
  parse_view1(session, os.path.join(basedir, 'view1', 'peopleDevTest.txt'), 'test')

  # Adds view2 people
  if verbose: print("Adding people from 'people.txt' ...")
  parse_view2(session, os.path.join(basedir, 'view2', 'people.txt'))

def add_pairs(session, basedir, verbose):
  """Adds the pairs for all protocols of the LFW database"""

  def add_mpair(session, protocol, file_id1, file_id2):
    """Add a matched pair to the LFW database."""
    session.add(Pair(protocol, file_id1, file_id2, True))

  def add_upair(session, protocol, file_id1, file_id2):
    """Add an unmatched pair to the LFW database."""
    session.add(Pair(protocol, file_id1, file_id2, False))

  def parse_file(session, list_filename, protocol):
    """Parses a file containing pairs and adds them to the LFW database"""
    pfile = open(list_filename)
    for line in pfile:
      llist = line.split()
      if len(llist) == 3: # Matched pair
        file_id1 = session.query(File).filter(File.name == filename(llist[0], int(llist[1]))).first().id
        file_id2 = session.query(File).filter(File.name == filename(llist[0], int(llist[2]))).first().id
        if verbose>1: print("  Adding matching pair ('%s', '%s')" % (file_id1, file_id2))
        add_mpair(session, protocol, file_id1, file_id2)
      elif len(llist) == 4: # Unmatched pair
        file_id1 = session.query(File).filter(File.name == filename(llist[0], int(llist[1]))).first().id
        file_id2 = session.query(File).filter(File.name == filename(llist[2], int(llist[3]))).first().id
        if verbose>1: print("  Adding unmatching pair ('%s', '%s')" % (file_id1, file_id2))
        add_upair(session, protocol, file_id1, file_id2)

  # flush session so that we get file ids
  session.flush()
  # Adds view1 pairs
  if verbose: print("Adding pairs from 'pairsDevTrain.txt' ...")
  parse_file(session, os.path.join(basedir, 'view1', 'pairsDevTrain.txt'), 'train')
  if verbose: print("Adding pairs from 'pairsDevTest.txt' ...")
  parse_file(session, os.path.join(basedir, 'view1', 'pairsDevTest.txt'), 'test')

  # Adds view2 pairs
  if verbose: print("Adding pairs from 'pairs_fold1.txt' ...")
  parse_file(session, os.path.join(basedir, 'view2', 'pairs_fold1.txt'), 'fold1')
  if verbose: print("Adding pairs from 'pairs_fold2.txt' ...")
  parse_file(session, os.path.join(basedir, 'view2', 'pairs_fold2.txt'), 'fold2')
  if verbose: print("Adding pairs from 'pairs_fold3.txt' ...")
  parse_file(session, os.path.join(basedir, 'view2', 'pairs_fold3.txt'), 'fold3')
  if verbose: print("Adding pairs from 'pairs_fold4.txt' ...")
  parse_file(session, os.path.join(basedir, 'view2', 'pairs_fold4.txt'), 'fold4')
  if verbose: print("Adding pairs from 'pairs_fold5.txt' ...")
  parse_file(session, os.path.join(basedir, 'view2', 'pairs_fold5.txt'), 'fold5')
  if verbose: print("Adding pairs from 'pairs_fold6.txt' ...")
  parse_file(session, os.path.join(basedir, 'view2', 'pairs_fold6.txt'), 'fold6')
  if verbose: print("Adding pairs from 'pairs_fold7.txt' ...")
  parse_file(session, os.path.join(basedir, 'view2', 'pairs_fold7.txt'), 'fold7')
  if verbose: print("Adding pairs from 'pairs_fold8.txt' ...")
  parse_file(session, os.path.join(basedir, 'view2', 'pairs_fold8.txt'), 'fold8')
  if verbose: print("Adding pairs from 'pairs_fold9.txt' ...")
  parse_file(session, os.path.join(basedir, 'view2', 'pairs_fold9.txt'), 'fold9')
  if verbose: print("Adding pairs from 'pairs_fold10.txt' ...")
  parse_file(session, os.path.join(basedir, 'view2', 'pairs_fold10.txt'), 'fold10')


def add_annotations(session, annotation_directory, annotation_extension, annotation_type, verbose):
  """Adds annotations of the given type from the given source directory."""
  session.flush()
  # get all files
  files = session.query(File)
  if verbose: print("Adding annotations of type '%s' from directory '%s'" % (annotation_type, annotation_directory))
  for file in files:
    # read annotations
    annotation_file = file.make_path(annotation_directory, annotation_extension)
    if not os.path.exists(annotation_file):
      if verbose: print("WARNING: Skipping non-existing annotation file '%s'" % annotation_file)
      continue

    if verbose>1: print("  Adding annotation file '%s'" % annotation_file)
    annotation_file_content = open(annotation_file).read()
    # add annotations to the session
    session.add(Annotation(file.id, annotation_type, annotation_file_content))


def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
  Client.metadata.create_all(engine)
  File.metadata.create_all(engine)
  People.metadata.create_all(engine)
  Pair.metadata.create_all(engine)
  Annotation.metadata.create_all(engine)

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
  add_files(s, args.basedir, args.verbose)
  add_people(s, args.basedir, args.verbose)
  add_pairs(s, args.basedir, args.verbose)
  if 'idiap' in args.annotation_types:
    add_annotations(s, args.idiap_annotation_dir, '.pos', 'idiap', args.verbose)
  if 'funneled' in args.annotation_types:
    add_annotations(s, args.funneled_annotation_dir, '.jpg.pts', 'funneled', args.verbose)

  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help='If set, I\'ll first erase the current database')
  parser.add_argument('-v', '--verbose', action='count', help='Do SQL operations in a verbose way?')
  parser.add_argument('-D', '--basedir', metavar='DIR', default='/idiap/resource/database/lfw', help='Change the relative path to the directory containing the images of the LFW database.')
  parser.add_argument('-F', '--funneled-annotation-dir', default='/idiap/group/biometric/annotations/lfw/funneled/lfw_funneled', help="Set the directory, where the funneled annotations for LFW images can be found")
  parser.add_argument('-I', '--idiap-annotation-dir', help="Set the directory, where Idiap's annotations for LFW images can be found")
  parser.add_argument('-a', '--annotation-types', nargs='*', choices=('idiap', 'funneled'), default=['funneled'], help='Choose, which kinds of annotations should be added to the database. Please note that the "idiap" annotations cannot be distributed outside Idiap.')

  parser.set_defaults(func=create) #action
