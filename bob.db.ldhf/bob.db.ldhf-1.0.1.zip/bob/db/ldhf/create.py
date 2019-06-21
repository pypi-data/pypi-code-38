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
This script creates the Long Distance Heterogeneous Face Database (LDHF-DB) in a single pass.
"""

import os

from .models import *
from .models import PROTOCOLS, GROUPS, PURPOSES

def add_clients(session, image_dir, verbose = True):

  """Adds the clients and split up the groups 'world', 'dev', and 'eval'"""
   
  path = os.path.join(image_dir, '1mNIR')#Using the directory 1mNIR as a reference

  for f in os.listdir(path):
     
    client_name = f.split("_")[0]
    if(client_name.find("dircksum")>0): continue #Removing the trash      
    client_id   = int(client_name)

    if verbose>=1: print("  Adding client {0}".format(client_name))


    session.add(Client(id=client_id,name=client_name))
  

def add_files(session, image_dir, annotation_dir, verbose = True):

  """Adds the Files"""
   

  dirs = ['1mNIR','1mVIS','60mNIR','60mVIS','100mNIR','100mVIS','150mNIR','150mVIS']
   
  file_id = 1
  for d in dirs:

    path = os.path.join(image_dir, d)

    if(path.find("NIR")>=0):
      modality = "NIR"
    else:
      modality = "VIS"       
    distance = d[0:-3]

    for f in os.listdir(path):
     
      client_name = f.split("_")[0]
      if(client_name.find("dircksum")>0): continue #Removing the trash            
      client_id   = int(client_name)
      image_name,_        = os.path.splitext(f)
      image_name = os.path.join(d,image_name)

      if verbose>=1: print("  Adding file {0}".format(image_name))


      session.add(File(file_id, client_id = client_id, image_name = image_name, modality=modality, distance=distance))
      add_annotations(session, file_id, os.path.join(annotation_dir,d,f)+".pos", verbose = verbose)
      file_id += 1



def add_annotations(session, file_id, annotation_filename, verbose = True):

  """Adds the Files"""
  annotations = open(annotation_filename).readlines()[0].rstrip("\n").split(" ")
  if verbose>=1: print("  Adding annotation {0}".format(annotation_filename))
  session.add(Annotation(file_id = file_id, re_x=annotations[2], re_y=annotations[3], le_x=annotations[0], le_y=annotations[1] ))




def add_protocols(session, verbose):
  """
  There are 10 protocols (10 splits VIS->NIR):
  
  According to the paper
  
  D. Kang, H. Han, A. K. Jain, and S.-W. Lee, "Nighttime Face Recognition at Large Standoff: Cross-Distance and Cross-Spectral Matching", Pattern Recognition, Vol. 47, No. 12, 2014, pp. 3750-3766.
  
  each protocol has 2 groups (world and dev) using 90% for trainin and 10% for testing
  
  Regarging the purposes, the 1m images are using for enrollment and the 1m, 15m, 100m, 150m images 

  """

  import numpy
  numpy.random.seed(10) #Fixing a seed
  
  offset = 0  # offset always ZERO since we have only train-dev (not eval)
  train_files = 50
  for p in PROTOCOLS:

    clients = list(range(1,101))
    numpy.random.shuffle(clients) #Shufling the 100 clients

    if verbose>=1: print("  Adding protocol {0}".format(p))

    #Selecting the clients for the split (90% training, 10% test)
    ##############
    # THE ORIGINAL PAPER USES AN EXTENSION OF THE SET OF VIS IMAGES FROM A PRIVATE DATASET,
    # CHECK PAGE 15 AND 26 OF THE PAPER.
    # HENCE I WILL ADAPT THE PROTOCOL AND USE 50 SAMPLES FOR TRAINING AND 50 SAMPLES FOR TESTING
    ##############
    
    dev_clients   = clients[offset : offset+train_files]
    insert_protocol_data(session, p, "dev", "", dev_clients)
    
    world_clients = list(set(clients).difference(set(dev_clients)))
    insert_protocol_data(session, p, "world", "train", world_clients)


def insert_protocol_data(session, protocol, group, purpose, clients_ids):

  db = bob.db.ldhf.Database();  

  for c_id in clients_ids:

    c = db.get_client_by_id(c_id)

    if purpose=="train":

      #Adding files for training
      for f in c.files:
        session.add(bob.db.ldhf.Protocol_File_Association(protocol, group, purpose, f.id, c.id))
         
    else:

      #Probing
      for c_id_probe in clients_ids:

        c_probe = db.get_client_by_id(c_id_probe)
      
        if(c_id==c_id_probe):

          #Here, I will select the 1m image to enroll and the rest for probing
          for f in c_probe.files:

            if((f.modality=="VIS") and (f.distance=="1m")):
              session.add(bob.db.ldhf.Protocol_File_Association(protocol, group, "enroll", f.id, c.id))
            elif(f.modality=="NIR"):
              session.add(bob.db.ldhf.Protocol_File_Association(protocol, group, "probe", f.id, c.id))
        
        else:
          #Only probes
          for f in c_probe.files:
            if(f.modality=="NIR"):
              session.add(bob.db.ldhf.Protocol_File_Association(protocol, group, "probe", f.id, c.id))



def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2));
  Client.metadata.create_all(engine)
  File.metadata.create_all(engine) 
  Annotation.metadata.create_all(engine)
  Protocol_File_Association.metadata.create_all(engine)
  

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
  add_clients(s, args.image_dir ,args.verbose)
  add_files(s, args.image_dir, args.annotation_dir ,args.verbose)  
  s.commit()
  add_protocols(s, args.verbose)

  #add_files(s, args.verbose)
  #add_annotations(s, args.annotation_dir, args.verbose)
  #add_protocols(s, args.verbose,photo2sketch=True)
  #add_protocols(s, args.verbose,photo2sketch=False)

  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-r', '--recreate', action='store_true', help='If set, I\'ll first erase the current database')
  parser.add_argument('-v', '--verbose', action='count', help='Increase verbosity?')
  parser.add_argument('-d', '--image-dir', default='', help="Change the relative path to the directory containing the images of the LDHF database.")
  parser.add_argument('-a', '--annotation-dir', default='./bob/db/ldhf/data/annotations',  help="The annotation directory. HAS TO BE THE SAME STRUCTURE AS PROVIDED BY THE DATABASE PROVIDERS (defaults to %(default)s)")

  parser.set_defaults(func=create) #action
