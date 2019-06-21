#!/usr/bin/env python 
# vim: set fileencoding=utf-8 : 
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch> 
# @date:   Mon 16 Nov 2015 16:11:56 CET 


"""
This file has some utilities to deal with the files provided by the database
"""

import os
import numpy
numpy.random.seed(0)
import pkg_resources


def read_annotations(file_name):
  """
  Read the annotations in the format

  X Y\n
  X Y\n
  .
  .
  .
  """
  original_annotations = open(file_name).readlines()
  annotations         = []
  
  for a in original_annotations:
    a = a.rstrip("\n").rstrip("\r")
    data = a.split(" ")
    if(len(data)!=2): #NEED TO HAVE ONLY 2 COORDINATES
      continue
    else:
      annotations.append(data)

  return annotations


class FERETWrapper():
  """
  Utility functions to deal with the FERET database.
  """

  def __init__(self, 
      photo_file_name = pkg_resources.resource_filename(__name__, "data/feret_filenames.txt")
   ):

    self.m_photo_file_name  = photo_file_name


  def get_clients_files(self):
    """
    Basically read the "feret_filenames.txt" file and extract the clients and the sketch and original file extensions
    
    The original client id is the first 5 chars of the "feret_filenames.txt" file
    
    First the sketh file after the photo file
    
    """
    raw_clients = open(self.m_photo_file_name).readlines()
    client_files = {}
    
    for c in raw_clients:
      c_id       = c[0:5]
      sketh_file = c[0:5]
      photo_file = c[0:-5]
      
      client_files[c[0:5]] = [sketh_file,photo_file]
    
    return client_files



  def get_clients_for_search(self):
    """
    The search protocol is based on the paper
    
    "Coupled Discriminant Feature Learning for Heterogeneous Face Recognition"
    TIFS-2015, Volume 10
    
    For that I shuffled the indexes of the 1194 clients and will take:
      - 700 subjects for training
      - 494 subjects for testing
    """
    
 
    clients  = range(1,1195)
    world = 700
    dev   = 494
    clients = list(clients)
    numpy.random.shuffle(clients)
    
    return clients[0:world], clients[world:world+dev] 


  def get_clients_for_verification(self):
    """
    The verification protocol was made by us
    
    For that I shuffled the indexes of the 1194 clients and will take:
    
      - 350 subjects for training
      - 350 subjects for development
      - 494 subjects for testing
    """
    
 
    clients  = range(1,1195)
    world  = 350
    dev    = 350
    test   = 494
    clients = list(clients)
    numpy.random.shuffle(clients)
    
    return clients[0:world], clients[world:world+dev], clients[world+dev:world+dev+test]



  def get_annotations(self, annotation_dir, annotation_extension='.dat'):
    """
    Get the annotation objects
    """

    db = bob.db.cuhk_cufs.Database()
    annotations = []
 
    for o in db.query(bob.db.cuhk_cufs.File).join(bob.db.cuhk_cufs.Client).filter(bob.db.cuhk_cufs.Client.original_database=="xm2vts"):
      #making the path
      if(o.modality=="sketch"):
        path = os.path.join(annotation_dir, o.path) + annotation_extension
      else:
        file_name = o.path.split("/")[2] #THE ORIGINAL XM2VTS RELATIVE PATH IS: XXX\XXX\XXX
        path = os.path.join(annotation_dir,"xm2vts", "photo", file_name) + "_f02" +  annotation_extension #FOR SOME REASON THE AUTHORS SET THIS '_f02 IN THE END OF THE FILE'

      #Reading the annotation file
      original_annotations = read_annotations(path)
      index = 0
      for a in original_annotations:
        
        annotations.append(bob.db.cuhk_cufs.Annotation(o.id, 
                                                  a[0],
                                                  a[1],
                                                  index = index
                                                 ))
        index += 1
    return annotations

