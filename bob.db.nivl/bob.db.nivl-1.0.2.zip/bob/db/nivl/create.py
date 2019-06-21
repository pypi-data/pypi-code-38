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
This script creates the Near-Infrared and Visible-Light (NIVL) Dataset in a single pass.


--- TEXT REMOVED FROM THE Readme.txt of the database -----

II.  NIVL Dataset Structure

The NIVL dataset spans multiple directories of images and metadata files that can be used as inputs to face recognition experiments.  There are three types of metadata files:

Image list - a sequence of paths to images of one subject photographed during a single session with a particular sensor, with one path per line.  A pair of image lists constitues a (non-)match pair if both lists correspond to the same (different) subject(s).

Image list collection - a sequence of paths to image lists, with one path per line.  An image list collection can describe the entries of a gallery or probe set.

Label list - a comma-separated value (CSV) listing of the subject identifiers for image lists.  A label list provides the information needed for determining which pairs of image lists match.  Each line of a label list should adhere to the following format:

{image list path},{subject identifier}


"""

import os

from .models import *
from .models import PROTOCOLS, GROUPS, PURPOSES
import pkg_resources


def _update(session, field):
  """Add, updates and returns the given field for in the current session"""
  session.add(field)
  session.flush()
  session.refresh(field)
  return field


def add_clients_files(session, image_dir, annotation_dir, verbose = True):
  """
  Add the clients and files in one single shot
  
  """

  label_files = ['D90-set-labels.csv','NIR-set-labels.csv'] # Files with the labels ({image list path},{subject identifier})
  
  clients  = {} #Controling the clients and the sessions captured for each client
  file_id_offset = 0
  
  for lf in label_files:

    if(lf.find("NIR") >= 0): 
      modality = "NIR"
    else:
      modality = "VIS"

    if verbose>=1: print("Adding labels {0}".format(lf))

    #opening each label file  
    labels = open(os.path.join(image_dir,lf)).readlines()
    
    for l in labels:
      image_list  = l.split(",")[0]
      client_name = l.split(",")[1].rstrip("\n")
    
      if(not client_name in clients):
        clients[client_name] = 1
        add_client(session, client_name, verbose=verbose)
      else:
        clients[client_name] += 1 #If the client already exists in the database, include the session

      year    = int(image_list.split("/")[2][0:4])
      capture_session = clients[client_name]
      file_id_offset = add_files(session, file_id_offset, client_name, os.path.join(image_dir,image_list), modality=modality, year=year, capture_session=capture_session,annotation_dir=annotation_dir, verbose=verbose)
  
      

def add_client(session, client_name, verbose = True):

  """Adds the clients and split up the groups 'world', 'dev', and 'eval'"""
  
  if verbose>=1: print("  Adding client {0}".format(client_name))  
  session.add(Client(id=client_name,group='world'))
  


def add_files(session, file_id_offset, client_name, image_list, modality, year, capture_session, annotation_dir, verbose = True):

  """Adds the Files from an image list"""
  
  images = open(image_list).readlines()
  for i in images:
    image_name,_ = os.path.splitext(i.rstrip("\n"))
    if verbose>=1: print("  Adding file {0}".format(image_name))      

    file_id_offset += 1
    f = File(file_id=file_id_offset, client_id = client_name, image_name = image_name, modality=modality, session=capture_session, year=year)
    session.add(f)
    session.flush()
    session.refresh(f)
    
    annotation_filename = os.path.join(annotation_dir, i.rstrip("\n")) + ".pos"
    add_annotations(session, file_id_offset, annotation_filename , verbose = True)
  return file_id_offset


def add_annotations(session, file_id, annotation_filename, verbose = True):

  """Adds the Files"""
  annotations = open(annotation_filename).readlines()[0].rstrip("\n").split(" ")
  if verbose>=1: print("  Adding annotation {0}".format(annotation_filename))
  session.add(Annotation(file_id = file_id, re_x=annotations[2], re_y=annotations[3], le_x=annotations[0], le_y=annotations[1] ))



def add_protocols_original(session, verbose = True):
  """
  Adding the two original protocols described in:
  
  Near-IR to Visible Light Face Matching: Effectiveness of Pre-Processing Options for Commercial Matchers
  
  
  For the first protocol, called `original_2011-2012` the VIS-2011 images are used as gallery and the NIR-2012 images are used as probes.
  For the first protocol, called `original_2012-2011` the VIS-2012 images are used as gallery and the NIR-2011 images are used as probes.
  
  """
  if verbose>=1: print("  Adding original protocols")

  galery_years = [2011,2012]
  probe_years  = [2012,2011]
  group   = "eval"
  purpose = "enroll"

  #Adding galery
  for i in range(len(galery_years)):
    galery = galery_years[i]
    probe  = probe_years[i]    
    protocol = "original_{0}-{1}".format(galery,probe)
   
    query = session.query(File) \
     .filter(File.year     == galery) \
     .filter(File.modality == 'VIS')

    for f in query.all():
      _update(session,Protocol_File_Association(protocol, group, purpose, f.id))


  #Adding probes
  purpose = "probe"  
  for i in range(len(galery_years)):
    galery = galery_years[i]
    probe = probe_years[i]
    
    protocol = "original_{0}-{1}".format(galery,probe)
   
    query = session.query(File) \
     .filter(File.year     == probe) \
     .filter(File.modality == 'NIR')

    for f in query.all():
      _update(session,Protocol_File_Association(protocol, group, purpose, f.id))



def add_protocol_comparison(session, verbose = True):
  """
  Adding the Idiap CUSTOMISED protocol
  
  This protocol uses:
    228 clients for evaluation
    171 clients for development set
    171 clients for training
  
    Here I will create 2 protocols:

     - idiap-comparison_2011-VIS-NIR
       - Training: 228 clients (pairs VIS-NIR)
       - Development: 171 clients. VIS Images from 2011 for enrollment and NIR images (both years) for probing
       - Evaluation: 171 clients. VIS Images from 2011 for enrollment and NIR images (both years) for probing
    

     - idiap-comparison_2012-VIS-NIR
       - Training: 228 clients (pairs VIS-NIR)
       - Development: 171 clients. VIS Images from 2012 for enrollment and NIR images (both years) for probing
       - Evaluation: 171 clients. VIS Images from 2012 for enrollment and NIR images (both years) for probing

   
    
    idiap-comparison
  """
  n_clients_per_group = {'world':229,
                         'dev':172,
                         'eval':173} #THE NUMBER OF CLIENTS IN EACH GROUP IS HARDCODED

  years_enroll = [2011,2012] #Defining the capture year of the enrollment data

  import numpy
  numpy.random.seed(10)  #Stabilizing the list
    
  for year in years_enroll:

    #Shuffle the clients
    client_indexes = range(574)
    numpy.random.shuffle(client_indexes)

    clients = session.query(Client).all();
    client_ids = [c.id for c in clients]

    offset = 0

    protocol = "idiap-comparison_%s-VIS-NIR" % year
    
    if verbose>=1: print("  Adding the protocol %s " % protocol)
    
    for g in GROUPS:

      clients_per_group = client_ids[offset:offset+n_clients_per_group[g]]
      offset += n_clients_per_group[g]
      
      if verbose>=1: print("    Group %s " % g)

      #Adding the world set data
      if (g=='world'):

        query = session.query(File) \
        .filter(File.client_id.in_(clients_per_group))
        
        for f in query.all():
          _update(session,Protocol_File_Association(protocol, g, "train", f.id))

      else:
      
        #Adding the enrollment data
        query = session.query(File) \
        .filter(File.client_id.in_(clients_per_group)) \
        .filter(File.modality == 'VIS') \
        .filter(File.year == year)
        
        for f in query.all():
          _update(session,Protocol_File_Association(protocol, g, "enroll", f.id))

        #Adding the probing data
        query = session.query(File) \
        .filter(File.client_id.in_(clients_per_group)) \
        .filter(File.modality == 'NIR')
        
        for f in query.all():
          _update(session,Protocol_File_Association(protocol, g, "probe", f.id))



def add_protocol_search(session, verbose = True):
  """
  Adding the Idiap CUSTOMISED SEARCH protocol
  
  This protocol uses:
    344 clients for training
    230 clients for development set
  
    Here I will create 10 protocols (split):

     - idiap-search_VIS-NIR_split[1-5]
       - Training: 344 clients (pairs VIS-NIR)
       - Development: 230 clients. VIS Images from 2011 for enrollment and NIR images (both years) for probing
                                   **** IF IS NOT POSSIBLE TO GET ONE IMAGE FROM 2011 FOR ENROLLMENT, GET THE FIRST FROM 2012 ****

  """
  n_clients_per_group = {'world':344,
                         'dev':230} #THE NUMBER OF CLIENTS IN EACH GROUP IS HARDCODED
  groups       = ["dev", "world"]

  import numpy
  numpy.random.seed(10)  #Stabilizing the list
    
  
  for split in range(1,6):
  

    #Shuffle the clients
    client_indexes = range(574)
    numpy.random.shuffle(client_indexes)

    clients = session.query(Client).all();
    client_ids = numpy.array([c.id for c in clients])

    offset = 0

    protocol = "idiap-search_VIS-NIR_split{0}".format(split)
    protocol_VIS = "idiap-search_VIS-VIS_split{0}".format(split) #Protocol to do VIS-VIS comparison
      
    
    if verbose>=1: print("  Adding the protocol %s " % protocol)
    
    for g in groups:

      indexes = client_indexes[offset:offset+n_clients_per_group[g]]
      clients_per_group = client_ids[indexes]
      offset += n_clients_per_group[g]
      
      if verbose>=1: print("    Group %s " % g)

      #Adding the world set data
      if (g=='world'):

        #Adding the VIS-NIR
        query = session.query(File) \
        .filter(File.client_id.in_(clients_per_group))        
        for f in query.all():
          _update(session,Protocol_File_Association(protocol, g, "train", f.id))

        #Adding the VIS-VIS
        query = session.query(File) \
        .filter(File.client_id.in_(clients_per_group))\
        .filter(File.modality == 'VIS')

        for f in query.all():
          _update(session,Protocol_File_Association(protocol_VIS, g, "train", f.id))

      else:
      
        ## Inserting each client
        for c in clients_per_group:

          #Adding the enrollment data - VIS-NIR and VIS-VIS
          ## FIRST TRY TO FIND SOME 2011 images
          query = session.query(File) \
          .filter(File.client_id==str(c)) \
          .filter(File.modality == 'VIS') \
          .filter(File.year == 2011)

          files = query.all()
          if(len(files) == 0):
            #IF DOES NOT HAVE ANY FILE FROM 2011, TAKE THE FIRST FROM 2012
            query = session.query(File) \
            .filter(File.client_id==str(c)) \
            .filter(File.modality == 'VIS') \
            .filter(File.year == 2012)

            files = query.all()
            assert len(files)>0
            files = [files[0]] #first from 2012

          for f in query.all():
            _update(session,Protocol_File_Association(protocol, g, "enroll", f.id))
            _update(session,Protocol_File_Association(protocol_VIS, g, "enroll", f.id))            


        #Adding the probing data - VIS-NIR
        query = session.query(File) \
        .filter(File.client_id.in_(clients_per_group)) \
        .filter(File.modality == 'NIR')

        for f in query.all():
          _update(session,Protocol_File_Association(protocol, g, "probe", f.id))


        #Adding the probing data - VIS-VIS
        query = session.query(File) \
        .filter(File.client_id.in_(clients_per_group)) \
        .filter(File.modality == 'VIS') \
        .filter(File.year == '2012')

        for f in query.all():
          _update(session,Protocol_File_Association(protocol_VIS, g, "probe", f.id))





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
  annotation_dir = pkg_resources.resource_filename(__name__, "./data/annotations/")
  add_clients_files(s, args.image_dir, annotation_dir, args.verbose)
  add_protocol_search(s, args.verbose)
  add_protocols_original(s, args.verbose)
  #add_protocol_comparison(s, args.verbose)

  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-r', '--recreate', action='store_true', help='If set, I\'ll first erase the current database')
  parser.add_argument('-v', '--verbose', action='count', help='Increase verbosity?')
  parser.add_argument('-d', '--image-dir', default='/idiap/resource/database/nivl/nivl-dataset-v1.0/', help="Change the relative path to the directory containing the images of the NIVL database.")

  parser.set_defaults(func=create) #action
