#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Tue 09 Oct 13:00:00 2014 CEST

"""
This script trains a PCA with 2 or more databases and plot the first 2 or 3 components in order to see the heterogeneous behaviour of databases.

MOVED FROM AN OLD PROJECT, PLEASE REFACTOR


"""
import bob.io.base
import bob.math
import imp
import argparse
import numpy
import os

import pkg_resources


def znorm(data):
  mu  = numpy.average(data,axis=0)
  std = numpy.std(data,axis=0)

  data = (data-mu)/std

  return data,mu,std


def split_modalities(files, separator):
  """
  Get a list of files and split in two lists given a separator string
  """

  #lists for each modality
  list_A = []
  list_B = []
      
  for f in files:

    if f.path.find(separator) > -1:
      list_A.append(f)
    else:
      list_B.append(f)
          
  return [list_A,list_B]
  
  
def load_file(file_name, flatten=True):

  d = bob.io.base.load(file_name)
  if len(d.shape) == 3: #Color image, convert to gray scale.
    d = bob.ip.color.rgb_to_gray(d)

  if(flatten):
    return d.flatten().astype(numpy.float64)
  else:
    return d.astype(numpy.float64)


def load_files_from_list(database, list_files, flatten=True):

  data    = load_file(os.path.join(database.original_directory,list_files[0].make_path()+database.original_extension), flatten=flatten)
  for i in range(1,len(list_files)):
    data = numpy.vstack((data, load_file(os.path.join(database.original_directory,list_files[i].make_path()+database.original_extension), flatten=flatten)))

  return data


def load_files(database, protocol, flatten=True, arrange_by_client=False, group="world"):

  if(arrange_by_client):
  
    ids = database.model_ids_with_protocol(protocol=protocol, groups=group)
    data = []

    for id in ids:

      files = database.objects(protocol=protocol, model_ids=id, groups=group, purposes='train')
      features = load_file(os.path.join(database.original_directory,files[0].make_path()+database.original_extension), flatten=flatten)
      for i in range(1,len(files)):
        features = numpy.vstack((features, load_file(os.path.join(database.original_directory,files[i].make_path()+database.original_extension), flatten=flatten)))

      data.append(features)
  
  else:
    files = database.objects(protocol=protocol, groups=group)
    data    = load_file(os.path.join(database.original_directory,files[0].make_path()+database.original_extension), flatten=flatten)
    for i in range(1,len(files)):
      data = numpy.vstack((data, load_file(os.path.join(database.original_directory,files[i].make_path()+database.original_extension), flatten=flatten)))

  return data  
  

def make_pca(data, components=2):

  T = bob.learn.linear.PCATrainer()
  #T = bob.trainer.PCATrainer()
  params = T.train(data) # params contain a tuple (eigenvecetors, eigenvalues) sorted in descending order
  #eigvalues = params[1]

  #energy = 0
  #components = min(components, eigvalues.shape[0])
  #for i in range(components):
  #  energy += eigvalues[i]
  #energy /= sum(eigvalues)

  # recalculating the shape of the LinearMachine
  #oldshape = params[0].shape
  #params[0].resize(oldshape[0], components)
  #return params[0], energy
  return params[0].weights[:,0:components]


def make_lda(data, components=2):

  T = bob.learn.linear.FisherLDATrainer(use_pinv=True)

  params = T.train(data) # params contain a tuple (eigenvecetors, eigenvalues) sorted in descending order
  eigvalues = params[1]

  energy = 0
  for i in range(components):
    energy += eigvalues[i]
  energy /= sum(eigvalues)

  # recalculating the shape of the LinearMachine
  oldshape = params[0].shape
  params[0].resize(oldshape[0], components)
  return params[0], energy



def GFK(Ps, Pt):

  import numpy

  N = Ps.shape[1]
  dim = Pt.shape[1]


  eps = 1e-20;

  #Principal angles
  QPt = numpy.dot(Ps.T, Pt)
   
  #[V1,V2,V,Gam,Sig] = gsvd(QPt(1:dim,:), QPt(dim+1:end,:));
  A = QPt[0:dim,:].copy()
  B = QPt[dim:,:].copy()
  
  [V1,V2,V,Gam,Sig] = bob.math.gsvd(A, B)
  V2 = -V2
  
  theta = numpy.arccos(numpy.diagonal(Gam))
  
  B1 = numpy.diag(0.5* (1+( numpy.sin(2*theta) / (2.*numpy.maximum
(theta,eps)))))
  B2 = numpy.diag(0.5*((numpy.cos(2*theta)-1) / (2*numpy.maximum(
theta,eps))))
  B3 = B2
  B4 = numpy.diag(0.5* (1-( numpy.sin(2*theta) / (2.*numpy.maximum
(theta,eps)))))


  delta1_1 = numpy.hstack( (V1, numpy.zeros(shape=(dim,N-dim))) )
  delta1_2 = numpy.hstack( (numpy.zeros(shape=(N-dim, dim)), V2) )
  delta1 = numpy.vstack((delta1_1, delta1_2))

  delta2_1 = numpy.hstack( (B1, B2,numpy.zeros(shape=(dim,N-2*dim)  )))
  delta2_2 = numpy.hstack( (B3, B4,numpy.zeros(shape=(dim,N-2*dim)  )))
  delta2_3 = numpy.zeros(shape=(N-2*dim, N))
  delta2 = numpy.vstack((delta2_1, delta2_2, delta2_3))

  delta3_1 = numpy.hstack((V1, numpy.zeros(shape=(dim,N-dim))))
  delta3_2 = numpy.hstack( (numpy.zeros(shape=(N-dim, dim)), V2))
  delta3 = numpy.vstack((delta3_1, delta3_2)).T

  delta = numpy.dot(numpy.dot(delta1, delta2), delta3)  
  G = numpy.dot(numpy.dot(Ps, delta), Ps.T)
    
  return G
  


numpy.random.seed(7)
#numpy.random.seed(9)

def main():

  RESOURCE_KEY = "database"
  databases = bob.bio.base.utils.resources.resource_keys(RESOURCE_KEY)

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('input_dir', type=str, default="./input/", help="The input path with the features or whatever you want to scatter (defaults to '%(default)s')")
  
  parser.add_argument('output_dir', type=str, default="./output/", help="The output path (defaults to '%(default)s')")
  
  parser.add_argument('-d', '--database',type=str, dest='database', default='', required=True, help='The database. The databases available: %s'%databases)

  parser.add_argument('-e','--extension', dest="extension", type=str, default=".hdf5", help="Files extension (defaults to '%(default)s')")  

  parser.add_argument('-s', '--split-string', type=str, dest='split_string', default='VIS',required=True, help = 'String to split the train set.')  
  
  parser.add_argument('-p', '--protocol',type=str, dest='protocol', default='default', help = 'Overwrite the default protocol (might not by applicable for all databases). WARNING!!! This parameter must match with the one in your database.')
  
  parser.add_argument('-o', '--modalities',type=str, dest='modalities', default=["VIS","NIR"], help='Image modalities in your training set, just for plotting', nargs=2)
  
  
  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')
  
  args = parser.parse_args()

  input_dir    = args.input_dir
  output_dir   = args.output_dir  
  verbose      = args.verbose
  
  protocol     = args.protocol
  split_string = args.split_string
  components   = 200
  database     = args.database
  extension    = args.extension
  modalities   = args.modalities
  
  bob.io.base.create_directories_safe(output_dir)

  database                    = bob.bio.base.utils.resources.load_resource(args.database, RESOURCE_KEY)
  database.original_directory = input_dir
  database.original_extension = extension

  d = 10

  print("Loading data ...")
  source_files, target_files = split_modalities(database.objects(protocol=protocol, groups="world"), split_string)

  #source       = load_files_from_list(database, source_files, flatten=True)
  #target       = load_files_from_list(database, target_files, flatten=True)
  
  # Normalizing the data
  print("Normalizing data ...")
  #source,_,_ = znorm(source[0:50])
  #target,_,_ = znorm(target[0:50])  
  
  #PCA for the source and the target
  print("Computing subspaces...")
  #Ps = make_pca(source, 50)
  #Pt = make_pca(target, 50)
  Ps = bob.io.base.load("source.hdf5")
  Pt = bob.io.base.load("target.hdf5")  

  G = GFK(Ps, Pt[:, 0:d])
  
  
  source_dev_files, target_dev_files = split_modalities(database.objects(protocol=protocol, groups="dev"), split_string)
  source_dev       = load_files_from_list(database, source_dev_files[0:10], flatten=True)

  
  #path = "/idiap/temp/tpereira/HTFace/CUHK-CUFS/GFK"
  #for s in source_dev_files:
  #  data = load_file(os.path.join(database.original_directory,s.make_path()+database.original_extension), flatten=True)
  #  feature = numpy.dot(data, Ps)        
  #  output_path = s.make_path(path) + database.original_extension
  #  bob.io.base.create_directories_safe(os.path.dirname(output_path))
  #  bob.io.base.save(feature, output_path)
  #    
  #target_dev       = load_files_from_list(database, target_dev_files, flatten=True)
  #for t in target_dev_files :
  #  data = load_file(os.path.join(database.original_directory,t.make_path()+database.original_extension), flatten=True)
  #  feature = numpy.dot(data, Pt)
  #  output_path = t.make_path(path) + database.original_extension
  #  bob.io.base.create_directories_safe(os.path.dirname(output_path))
  #  bob.io.base.save(feature, output_path)



if __name__ == '__main__':
  main()
