#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Fri May 11 17:20:46 CEST 2012
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

"""This script creates the GBU database in a single pass.
"""

from __future__ import print_function

import os

from .models import *
from bob.db.base import utils


def collect_files(directory, extension = '.jpg', subdirectory = None):
  """Reads add images (in all sub-directories) of the given directory and
  corrects the directories stored in all entries"""
  # recursively walk through the directory and collect files
  walk = [(x[0], x[1], x[2]) for x in os.walk(directory)]

  # split off the images and align the directory
  filelist = []
  dirlist = []
  for dir,subdirs,files in walk:
    filelist.extend([f for f in files if os.path.splitext(f)[1]==extension and ((not subdirectory) or subdirectory in dir)])
    dirlist.extend([dir.lstrip(directory) for f in files if os.path.splitext(f)[1]==extension and ((not subdirectory) or subdirectory in dir)])

  return (filelist, dirlist)


def add_files_and_protocols(session, list_dir, image_dir, verbose):
  """Add files, clients and protocols to the GBU database."""

  import xml.sax
  class XmlFileReader (xml.sax.handler.ContentHandler):
    def __init__(self):
      self.m_signature = None
      self.m_path = None
      self.m_presentation = None
      self.m_file_list = []

    def startDocument(self):
      pass

    def endDocument(self):
      pass

    def startElement(self, name, attrs):
      if name == 'biometric-signature':
        self.m_signature = attrs['name']
      elif name == 'presentation':
        self.m_path = os.path.splitext(attrs['file-name'])[0]
        self.m_presentation = attrs['name']
      else:
        pass

    def endElement(self, name):
      if name == 'biometric-signature':
        # assert that everything was read correctly
        assert self.m_signature is not None and self.m_path is not None and self.m_presentation is not None
        # add a file to the sessions
        self.m_file_list.append(File(self.m_presentation, self.m_signature, self.m_path))
        # new file
        self.m_presentation = self.m_signature = self.m_path = None
      else:
        pass

  ################################################################################
  ##### End of XmlFileReader class ###############################################


  def read_list(xml_file, eye_file = None):
    """Reads the xml list and attaches the eye files, if given"""
    # create xml reading instance
    handler = XmlFileReader()
    xml.sax.parse(xml_file, handler)
    return handler.m_file_list


  def correct_dir(image_list, filenames, directories, extension = '.jpg'):
    """Iterates through the image list and corrects the directory"""
    # first, collect entries in a faster structure
    image_dict = {}
    for i in image_list:
      image_dict[os.path.basename(i.path) + extension] = i
    # assert that we don't have duplicate entries
    assert len(image_dict) == len(image_list)

    # now, iterate through the directory list and check for the file names
    for index in range(len(filenames)):
      if filenames[index] in image_dict:
        # copy the directory of the found image
        image_dict[filenames[index]].path = os.path.join(directories[index], image_dict[filenames[index]])

    # finally, do the other way around and check if every file has been found
    filenames_set = set()
    for f in filenames:
      filenames_set.add(f)
    # assert that we don't have duplicate entries
    assert len(filenames) == len(filenames_set)

    missing_files = []
    for i in image_list:
      if os.path.basename(i.path) + extension not in filenames_set:
        missing_files.append(i)
        print("The image '" + i.m_filename + extension + "' was not found in the given directory")

    return missing_files



###########################################################################
#### Here the function really starts ######################################

  # first, read the file lists from XML files
  sub_worlds = Subworld.subworld_choices
  protocols = Protocol.protocol_choices

  train_lists = {}
  target_lists = {}
  query_lists = {}

  for p in sub_worlds:
    # Training files
    train_lists[p] = read_list(os.path.join(list_dir, 'GBU_Training_Uncontrolled%s.xml'%p))

  for p in protocols:
    # Target files
    target_lists[p] = read_list(os.path.join(list_dir, 'GBU_%s_Target.xml'%p))
    # Query files
    query_lists[p] = read_list(os.path.join(list_dir, 'GBU_%s_Query.xml'%p))
  all_lists = [f for f in train_lists.values()] + [f for f in target_lists.values()] + [f for f in query_lists.values()]

  # now, correct the directories according to the real image directory structure
  if image_dir:
    if verbose: print("Collecting images from directory", image_dir, "...", end=' ')
    # collect all the files in the given directory
    file_list, dir_list = collect_files(image_dir)
    if verbose: print("done. Collected", len(file_list), "images.")
    # correct the directories in all file lists
    for l in all_lists:
      correct_dir(l, file_list, dir_list)

  # Now, create file entries in the database and create clients and files
  clients = set()
  files = {}
  if verbose: print("Adding clients and files ...")
  for list in all_lists:
    for file in list:
      if file.signature not in clients:
        if verbose>1: print("  Adding client '%s'" % file.signature)
        session.add(Client(file.signature))
        clients.add(file.signature)
      if file.presentation not in files:
        if verbose>1: print("  Adding file '%s'" % file.presentation)
        session.add(file)
        files[file.presentation] = file

  # training sets
  if verbose: print("Adding subworlds ...")
  for name,list in train_lists.items():
    # add subworld
    subworld = Subworld(name)
    session.add(subworld)
    session.flush()
    session.refresh(subworld)
    for file in list:
      if verbose>1: print("  Adding file '%s' to subworld '%s'" % (file.presentation, name))
      subworld.files.append(files[file.presentation])

  # protocols
  if verbose: print("Adding protocols ...")
  for protocol in protocols:
    target_protocol = Protocol(protocol, 'enroll')
    session.add(target_protocol)
    session.flush()
    session.refresh(target_protocol)
    # enroll files
    for file in target_lists[protocol]:
      if verbose>1: print("  Adding file '%s' to target protocol '%s'" % (file.presentation, protocol))
      target_protocol.files.append(files[file.presentation])

    # probe files
    query_protocol = Protocol(protocol, 'probe')
    session.add(query_protocol)
    session.flush()
    session.refresh(query_protocol)
    for file in query_lists[protocol]:
      if verbose>1: print("  Adding file '%s' to query protocol '%s'" % (file.presentation, protocol))
      query_protocol.files.append(files[file.presentation])

  # annotations
  # for speed purposes, create a special dictionary from file name to file id
  if verbose: print("Adding annotations ...")
  file_id_dict = {}
  for file in files.values():
    file_id_dict[os.path.basename(file.path)] = file.id
  # read the eye position list
  eyes_file = os.path.join(list_dir, 'alleyes.csv')
  f = open(eyes_file)
  for line in f:
    # skip first line
    entries=line.split(',')
    assert len(entries) == 5
    name = os.path.splitext(os.path.basename(entries[0]))[0]
    # test if these eye positions belong to any file of this list
    if name in file_id_dict:
      if verbose>1: print("  Adding annotation '%s' to query file '%s'" % ([int(e.strip()) for e in entries[1:]], name))
      session.add(Annotation(file_id_dict[name], entries[1:]))


  # all right, that should be it.

def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
  Base.metadata.create_all(engine)


def unzip_file(file_name):
  """Unzip the XMLs"""
  import tarfile

  t = tarfile.open(fileobj=open(file_name), mode='r:gz')
  path = os.path.join(os.path.dirname(file_name), 'xmls')
  t.extractall(path)
  t.close()

  return path


# Driver API
# ==========

def create(args):
  """Creates or re-creates this database"""

  dbfile = args.files[0]

  if args.recreate:
    if args.verbose and os.path.exists(dbfile):
      print('unlinking %s...' % dbfile)
    if os.path.exists(dbfile): os.unlink(dbfile)

  if not os.path.exists(os.path.dirname(dbfile)):
    os.makedirs(os.path.dirname(dbfile))

  # the real work...
  create_tables(args)
  s = utils.session(args.type, args.files[0], echo=(args.verbose > 2))
  if os.path.isfile(args.list_directory):
    path = unzip_file(args.list_directory)
  else:
    path = args.list_directory
  
  add_files_and_protocols(s,path , args.rescan_image_directory, args.verbose)
  s.commit()
  s.close()


def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  import pkg_resources

  parser = subparsers.add_parser('create', help=create.__doc__)
  xml_paths = pkg_resources.resource_filename(__name__, 'xmls.tar.gz')
  parser.add_argument('-R', '--recreate', action='store_true', help='If set, I\'ll first erase the current database')
  parser.add_argument('-v', '--verbose', action='count', help='Do SQL operations in a verbose way')
  parser.add_argument('-D', '--list-directory', metavar='DIR', default = xml_paths, help='Change the relative path to the directory containing the list of the GBU database. Defaults to "%(default)s"')
  # here at Idiap, we can use the  directory '/idiap/resource/database/MBGC-V1' to re-scan, if required.
  parser.add_argument('--rescan-image-directory', metavar='DIR', help='If required, select the path to the directory containing the images of the MBGC-V1 database to be re-scanned')

  parser.set_defaults(func=create) #action
