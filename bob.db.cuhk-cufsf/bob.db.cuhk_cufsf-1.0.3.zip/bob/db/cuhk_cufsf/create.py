#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# @date:   Tue Aug  11 14:07:00 CEST 2015
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
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

"""
This script creates the CUHK-CUFS database in a single pass.
"""

import os

from .models import *
from .utils import FERETWrapper
import pkg_resources

def add_clients_files_annotations(session, verbose = True):

  """
   Adds the clients and the files
   
   Returns a map with the client_id as a key with a list its file ids
  """
   
  #Adding the clients from XM2VTS
  feret          = FERETWrapper()
  feret_clients  = feret.get_clients_files()

  output = {} 

  if verbose>=1: print('Adding FERET clients and files to the database ...')
    
  client_id_offset = 0
  file_id_offset   = 0  
  for c in feret_clients:

    client_id_offset   += 1
    original_client_id = c
 
    if verbose>=1: print("  Adding client {0}".format(original_client_id))   
    session.add(Client(id=client_id_offset, 
                       original_id = original_client_id
                ))
     
    #Adding sketch
    file_id_offset += 1
    session.add(File(id=file_id_offset, 
                     image_name=feret_clients[c][0],
                     client_id = client_id_offset,
                     modality="sketch"
                ))                
    output[client_id_offset] = [file_id_offset]

    r_annotations = open(pkg_resources.resource_filename(__name__, "data/sketch_points/{0}.3pts".format(feret_clients[c][0]))).readlines()[0].rstrip("\n").split(" ") 
    l_annotations = open(pkg_resources.resource_filename(__name__, "data/sketch_points/{0}.3pts".format(feret_clients[c][0]))).readlines()[1].rstrip("\n").split(" ")
    session.add(Annotation(file_id = file_id_offset, re_x=r_annotations[0], re_y=r_annotations[1], le_x=l_annotations[0], le_y=l_annotations[1] ))

    
    
    #Adding photo
    file_id_offset += 1
    session.add(File(id=file_id_offset, 
                     image_name=feret_clients[c][1],
                     client_id = client_id_offset,
                     modality="photo"
                ))
    output[client_id_offset].append(file_id_offset)
    annotations = open(pkg_resources.resource_filename(__name__, "data/photo_points/{0}.tif.pos".format(feret_clients[c][1]))).readlines()[0].rstrip("\n").split(" ")
    session.add(Annotation(file_id = file_id_offset, re_x=annotations[2], re_y=annotations[3], le_x=annotations[0], le_y=annotations[1] ))
    

  return output



def add_search_protocols(session, verbose, clients):

  protocols = ['search_split1','search_split2','search_split3','search_split4','search_split5']
  feret          = FERETWrapper()
  for p in protocols:
  
    if verbose>=1: print("  Adding protocol {0}".format(p)) 
  
    world, dev = feret.get_clients_for_search()


    #Adding training set
    for w in world:
      
      for f in clients[w]:
        #ADDING PHOTO -> SKETCH
        protocol = "{0}_p2s".format(p)
        session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                    protocol,
                    "world",
                    "train", 
                    f))

        #ADDING PHOTO <- SKETCH
        protocol = "{0}_s2p".format(p)        
        session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                    protocol,
                    "world",
                    "train", 
                    f))

    #Adding dev set
    for d in dev:
      
      #ADDING PHOTO -> SKETCH 
      # ENROLL
      protocol = "{0}_p2s".format(p)
      session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                  protocol,
                  "dev",
                  "enroll", 
                  clients[d][1]))

      #ADDING PHOTO -> SKETCH
      # PROBE
      session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                    protocol,
                    "dev",
                    "probe", 
                    clients[d][0]))



      #ADDING PHOTO <- SKETCH 
      # ENROLL
      protocol = "{0}_s2p".format(p)
      session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                  protocol,
                  "dev",
                  "enroll", 
                  clients[d][1]))

      #ADDING PHOTO <- SKETCH
      # PROBE
      session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                    protocol,
                    "dev",
                    "probe", 
                    clients[d][0]))



def add_verification_protocols(session, verbose, clients):

  protocols = ['idiap_verification']
  feret          = FERETWrapper()
  for p in protocols:
  
    if verbose>=1: print("  Adding protocol {0}".format(p)) 
  
    world, dev, test = feret.get_clients_for_verification()

    #Adding training set
    for w in world:
      
      for f in clients[w]:
        #ADDING PHOTO -> SKETCH
        protocol = "{0}_p2s".format(p)
        session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                    protocol,
                    "world",
                    "train", 
                    f))

        #ADDING PHOTO <- SKETCH
        protocol = "{0}_s2p".format(p)        
        session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                    protocol,
                    "world",
                    "train", 
                    f))
        

    #Adding dev set
    for d in dev:
      
      #ADDING PHOTO -> SKETCH 
      # ENROLL
      protocol = "{0}_p2s".format(p)
      session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                  protocol,
                  "dev",
                  "enroll", 
                  clients[d][1]))

      #ADDING PHOTO -> SKETCH
      # PROBE
      session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                    protocol,
                    "dev",
                    "probe", 
                    clients[d][0]))



      #ADDING PHOTO <- SKETCH 
      # ENROLL
      protocol = "{0}_s2p".format(p)
      session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                  protocol,
                  "dev",
                  "enroll", 
                  clients[d][1]))

      #ADDING PHOTO <- SKETCH
      # PROBE
      session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                    protocol,
                    "dev",
                    "probe", 
                    clients[d][0]))      


    #Adding eval set
    for t in test:
      
      #ADDING PHOTO -> SKETCH 
      # ENROLL
      protocol = "{0}_p2s".format(p)
      session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                  protocol,
                  "eval",
                  "enroll", 
                  clients[t][1]))

      #ADDING PHOTO -> SKETCH
      # PROBE

      session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                    protocol,
                    "eval",
                    "probe", 
                    clients[t][0]))



      #ADDING PHOTO <- SKETCH 
      # ENROLL
      protocol = "{0}_s2p".format(p)
      session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                  protocol,
                  "eval",
                  "enroll", 
                  clients[t][1]))

      #ADDING PHOTO <- SKETCH
      # PROBE
      session.add(bob.db.cuhk_cufsf.Protocol_File_Association(
                    protocol,
                    "eval",
                    "probe", 
                    clients[t][0]))



def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2));
  Client.metadata.create_all(engine)
  File.metadata.create_all(engine) 
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
  s = session_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2))
  
  clients = add_clients_files_annotations(s, args.verbose)

  add_search_protocols(s, args.verbose, clients)
  add_verification_protocols(s, args.verbose, clients)
 
  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-r', '--recreate', action='store_true', help='If set, I\'ll first erase the current database')
  parser.add_argument('-v', '--verbose', action='count', help='Increase verbosity?')
  parser.add_argument('-s', '--sketch-dir', default='.',  help="The directory that contains the CUFSF (defaults to %(default)s)")
  

  parser.set_defaults(func=create) #action
