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
This script creates the Polarimetric Thermal Database Dataset in a single pass.


"""

import os

from .models import *
from .models import PROTOCOLS, GROUPS, PURPOSES
import pkg_resources
import numpy
numpy.random.seed(10)


def parse_file_name(file_name):
  """
    Parse the filenames  
    VIS - ANN_XXXYY_Z_VI_fMM
    
    The images has the following pattern

    ANN_XXXYY_Z_VI_fMM like this example (A01_IOD87_B_VI_f01.png) where:
    - NN is the client id
    - XXXYY means inter-ocular distance (XXX) and distance (YY)
    - Z is the condition B=Baseline (neutral expression) and E=Expression (the clients where asked to count from 1 to n)
    - VI means visible spectra
    - MM is the shot (from 1-4)
        
    
    THERMAL - ANN_RM_Z_XX_fWW where:
    - NN is the client id
    - M is the range (1-3 (2.5m, 5m, 7.5m))
    - Z is the condition B=Baseline (neutral expression) and E=Expression (the clients where asked to count from 1 to n)
    - XX is the type of the polarization (S0 (real thermal), S1, S2, DP (DoLP))
    - WW is the shot (from 1-4)
  """

  elements = file_name.split("_")
  if file_name.find("_VI_") > 0:
    client = elements[0]
    capture_range = "R1"
    condition = elements[2]
    polarization = "VIS"
    shot = elements[4]
    modality = "VIS"
  else:
    client = elements[0]
    capture_range = elements[1]
    condition = elements[2]
    polarization = elements[3]
    shot = elements[4]
    modality = "THERMAL"
    
  return client, capture_range, condition, polarization, shot, modality


def add_clients_files(session, image_dir, verbose = True):
  """
  Add the clients and files in one single shot
  
  """

  annotations_r = [65, 106]
  annotations_l = [140, 106]

  directories = ['Visible/IOD87_B/', 'Visible/IOD87_E/', 'Polarimetric/'] # Files with the labels ({image list path},{subject identifier})

  clients  = {} #Controling the clients and the sessions captured for each client
  file_id_offset = 0

  # Navigating in the direcoty
  for d in directories:  
    for f in os.listdir(os.path.join(image_dir, d)):
  
      file_name, extension = os.path.splitext(f)
      
      # Adding only PNG
      if extension==".png" and file_name.find("_S1_") < 0 and file_name.find("_S2_") < 0 :
        client, capture_range, condition, polarization, shot, modality = parse_file_name(file_name)
      
        # Adding client
        if(not client in clients):
          clients[client] = []
          if verbose>=1: print("  Adding client {0}".format(client))
          session.add(Client(id=client))

        file_name = d + file_name
        if verbose>=1: print("  Adding file {0}".format(file_name))
        file_id_offset += 1
        f = File(file_id=file_id_offset,
                 client_id = client,
                 image_name = file_name,
                 modality=modality,
                 polarization=polarization,
                 shot=shot)
        session.add(f)
        session.add(Annotation(file_id = file_id_offset, re_x=annotations_r[0], re_y=annotations_r[1], le_x=annotations_l[0], le_y=annotations_l[1]))
        clients[client].append(f)

  return clients


def add_protocols (session, clients, split_number, verbose):

  client_keys = clients.keys()
  numpy.random.shuffle(client_keys)

  train_clients = range(len(client_keys))[0:25]
  test_clients = range(len(client_keys))[25:]
  
  polarization = ['VIS', 'polarimetric', 'thermal']
  expression = ['overall', 'expression', 'R1', 'R2', 'R3']
  
  for p in polarization:
    for e in expression:
    
      if p == 'VIS':
        protocol = 'VIS-VIS-split{0}'.format(split_number)
        p_file = 'VIS'
      else:
        protocol = 'VIS-{0}-{1}-split{2}'.format(p, e, split_number)

        if p == 'polarimetric':
          p_file = 'DP'
        else:
          p_file = 'S0'

      # Just to have one VIS-VIS protocol
      if p == "VIS" and e !='overall':
        continue

      if verbose>=1: print("Adding protocol {0}".format(protocol))

      # Adding world
      for k in train_clients:
        add_world(session, clients[client_keys[k]], protocol, p_file)
        
      # Adding dev
      for k in test_clients:
        add_dev(session, clients[client_keys[k]], protocol, p_file)
      

def add_world(session, client_files, protocol, polarization):
  for f in client_files:
    if polarization in f.path or f.polarization=='VIS':
      session.add(Protocol_File_Association(protocol, "world", "train", f.id))


def add_dev(session, client_files, protocol, polarization):
  for f in client_files:
  
    # VIS and neutral expression for enroll always
    if f.modality == 'VIS' and '_B_' in f.path:
      session.add(Protocol_File_Association(protocol, "dev", "enroll", f.id))

    # VIS and expression as probe in a VIS-VIS protocol 
    elif f.modality == 'VIS' and '_E_' in f.path and 'VIS-VIS' in protocol:
      session.add(Protocol_File_Association(protocol, "dev", "probe", f.id))
    
    #### Only thermal images reaches this point ####
    
    # If the protocol is overall, add the probe
    elif 'overall' in protocol and polarization == f.polarization:
      session.add(Protocol_File_Association(protocol, "dev", "probe", f.id))
    
    # If protocol is 'expression', add only '_E_' images
    elif 'expression' in protocol and '_E_' in f.path and polarization == f.polarization:
      session.add(Protocol_File_Association(protocol, "dev", "probe", f.id))

    # Adding the ranges as probes

    elif 'R1' in protocol and '_R1_' in f.path and polarization == f.polarization:
      session.add(Protocol_File_Association(protocol, "dev", "probe", f.id))

    elif 'R2' in protocol and '_R2_' in f.path and polarization == f.polarization:
      session.add(Protocol_File_Association(protocol, "dev", "probe", f.id))

    elif 'R3' in protocol and '_R3_' in f.path and polarization == f.polarization:
      session.add(Protocol_File_Association(protocol, "dev", "probe", f.id))

def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2));
  Client.metadata.create_all(engine)
  File.metadata.create_all(engine) 
  Annotation.metadata.create_all(engine)
  #Protocol_File_Association.metadata.create_all(engine)


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
  clients = add_clients_files(s, args.image_dir, args.verbose)
  s.commit()
  
  for i in range(1,6):
    add_protocols(s, clients, i, args.verbose)

  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-r', '--recreate', action='store_true', help='If set, I\'ll first erase the current database')
  parser.add_argument('-v', '--verbose', action='count', help='Increase verbosity?')
  parser.add_argument('-d', '--image-dir', default='/idiap/project/hface/databases/polimetric_thermal_database/Registered/', help="Change the relative path to the directory containing the images of the Polarimetric database.")

  parser.set_defaults(func=create) #action
