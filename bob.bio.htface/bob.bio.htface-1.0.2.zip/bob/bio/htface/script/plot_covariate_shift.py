#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Tue 09 Oct 13:00:00 2014 CEST

"""
This script trains a PCA with 2 or more databases and plot the first 2 or 3 components in order to see the heterogeneous behaviour of databases.

MOVED FROM AN OLD PROJECT, PLEASE REFACTOR


"""
import bob
import bob.io.base
import matplotlib
#from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as mpl

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
  eigvalues = params[1]

  energy = 0
  components = min(components, eigvalues.shape[0])
  for i in range(components):
    energy += eigvalues[i]
  energy /= sum(eigvalues)

  # recalculating the shape of the LinearMachine
  oldshape = params[0].shape
  params[0].resize(oldshape[0], components)
  return params[0], energy


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
  

def mean_shift(data_A, data_B):
  """
  Compute the mean shift between two dataset A and B
  
  Basically the shift is mu_A - mu_B
  
  Parameters:
 
  data_A
    Data from dataset A

  data_B
    Data from dataset B
    
  """  

  mu_A = numpy.mean(data_A, axis=0)
  mu_B = numpy.mean(data_B, axis=0)
  
  return mu_B - mu_A
  


def map_shift(data_A, data_B, relevance_factor=1.1):
  """
  Compute the shift between two dataset A and B using the Maximum a Posteriori point estimator.
  
  Parameters:
 
  data_A
    Data from dataset A

  data_B
    Data from dataset B
    
  """  

  import bob.learn.em
  prior = bob.learn.em.GMMMachine(1,data_A.shape[1])
  prior.means     = numpy.array([numpy.mean(data_A, axis=0)])
  prior.variances = numpy.array([numpy.std(data_A, axis=0)**2])  

  map_machine = bob.learn.em.GMMMachine(1,data_B.shape[1])
  #map_trainer = bob.learn.em.MAP_GMMTrainer(prior, relevance_factor=relevance_factor, update_means=True, update_variances=False, update_weights=False)
  map_trainer = bob.learn.em.MAP_GMMTrainer(prior, alpha=relevance_factor, update_means=True, update_variances=False, update_weights=False)  
  bob.learn.em.train(map_trainer, map_machine, data_B, max_iterations=50)

  return map_machine.means[0,:]


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
  
  parser.add_argument('--shift-alg', type=str, dest="shift_alg", choices=['mean','map','none'], default="mean", help="The type of covariate shift!")
  
  parser.add_argument('-c', '--colors', type=str, dest='colors', default=["r.","y."], help='Colors for plotting', nargs=2)
    
  parser.add_argument('-t','--title', type=str, dest="title", default="Scatter plot between two different acquisition modalities", help="Plot title")

  parser.add_argument('-m','--machine', type=str, dest="machine", default="", help="Linear machine path (defaults to '%(default)s')")
  
  parser.add_argument('-l', '--lda', action='store_true', dest='lda', default=False, help='Runs LDA')
  
  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')
  
  args = parser.parse_args()

  input_dir    = args.input_dir
  output_dir   = args.output_dir  
  verbose      = args.verbose
  machine_file = args.machine
  colors       = args.colors
  title        = args.title
  
  protocol     = args.protocol
  split_string = args.split_string
  machine      = args.machine
  components   = 2
  database     = args.database
  extension    = args.extension
  modalities   = args.modalities
  
  lda          = args.lda
  shift_alg     = args.shift_alg

  bob.io.base.create_directories_safe(output_dir)

  database                    = bob.bio.base.utils.resources.load_resource(args.database, RESOURCE_KEY)
  database.original_directory = input_dir
  database.original_extension = extension


  matplotlib.use('pdf') #avoids TkInter threaded start
  from matplotlib.backends.backend_pdf import PdfPages
  pp = PdfPages(os.path.join(output_dir,"scatter.pdf"))

  fig = mpl.figure()

  if(machine_file==""):

    if(verbose):
      print("Loading training set...")
    
    training_data  = load_files(database, protocol, flatten=True, arrange_by_client=False, group="world")
    training_data,mu,std   = znorm(training_data)

    if lda:

      training_data_client  = load_files(database, protocol, flatten=True, arrange_by_client=True, group="world")
      pca_machine, energy   = make_pca(training_data, components=100)
      
      training_data_client_projected = []
      for c in training_data_client:
        training_data_client_projected.append(pca_machine(c))

      #training_data,mu,std   = znorm(training_data)
      lda_machine, energy        = make_lda(training_data_client_projected, components=components)

      new_U = numpy.dot(pca_machine.weights, lda_machine.weights)
      machine = bob.learn.linear.Machine(input_size=new_U.shape[0], output_size=new_U.shape[1])
      machine.weights = new_U      
      machine.input_divide   = std
      machine.input_subtract = mu
      
      hdf5file = bob.io.base.HDF5File(os.path.join(output_dir,"pca_lda.hdf5"),"w")
      hdf5file.set('energy', energy)
      machine.save(hdf5file)
    
    else:

      #training
      #if(verbose):
      #  print("Doing PCA. Matrix [{0} x {1}] ... ".format(training_data.shape[0],training_data.shape[1]))

      machine, energy        = make_pca(training_data, components=components)
      machine.input_divide   = std
      machine.input_subtract = mu

      hdf5file = bob.io.base.HDF5File(os.path.join(output_dir,"pca.hdf5"),"w")
      hdf5file.set('energy', energy)
      machine.save(hdf5file)
    
      #print "Energy accumulated in the first two components {0}%".format(energy * 100)
    
      del training_data
      
  else:
    hdf5file = bob.io.base.HDF5File(machine_file)
    machine  = bob.learn.linear.Machine(hdf5file)

    energy           = hdf5file.read('energy')
    #print "Energy accumulated in the first two components {0}%".format(energy * 100)
    

  #Ploting
  mpl.title(title)
  ax = mpl.axes()

  files_A, files_B = split_modalities(database.objects(protocol=protocol, groups="world"), split_string)

  #if(verbose):
  #  print("Loading dev data ...")


  data_A       = load_files_from_list(database, files_A[0:1000], flatten=True)
  projected_data_A = machine(data_A)
  del data_A
    
  data_B       = load_files_from_list(database, files_B[0:1000], flatten=True)
  projected_data_B = machine(data_B)
  del data_B

  if(verbose):
    print("Ploting ...")
  mpl.plot(projected_data_A[:,0],projected_data_A[:,1], colors[0], label=modalities[0])
  mpl.plot(projected_data_B[:,0],projected_data_B[:,1], colors[1], label=modalities[1])


  #### sketch  
  #mpl.text(-30, -60, r'$\{$', fontsize=100, rotation=90)
  #mpl.text(-20, -48, '$X_A$', fontsize=20)

  #mpl.text(5, -60, r'$\{$', fontsize=100, rotation=90)
  #mpl.text(14, -48, '$X_B$', fontsize=20)
  
  #mpl.text(-16, -58, '$X\'_{SKE} = X_{VIS} + (\mu_{SKE} - \mu_{VIS})$', fontsize=20)
  #mpl.text(-16, -58, '$X\'_{SKE} = X_{VIS} + \\theta_{MAP}$', fontsize=20)
  #mpl.text(-16, -68, '$score = d(X\'_{SKE}, X_{SKE})$', fontsize=20)


  """
  #### VIS-NIR
  mpl.text(-40, -45, r'$\{$', fontsize=100, rotation=90)
  mpl.text(-30, -38, '$X_B$', fontsize=20)

  mpl.text(0, -45, r'$\{$', fontsize=100, rotation=90)
  mpl.text(10, -38, '$X_A$', fontsize=20)
  """    
  #mpl.text(-59, 35, '$X\'_{NIR} = X_{VIS} + (\mu_{NIR} - \mu_{VIS})$', fontsize=20)
  #mpl.text(-59, 35, '$X\'_{NIR} = X_{VIS} + \\theta_{MAP}$', fontsize=20)
  #mpl.text(-59, 29, '$score = d(X\'_{NIR}, X_{NIR})$', fontsize=20)

  
  

  #Selecting the shift algorithm
  if shift_alg=="mean":
    shift = mean_shift(projected_data_A, projected_data_B)
  elif shift_alg=="map":
    shift = map_shift(projected_data_A, projected_data_B)
  elif shift_alg=="none":
    shift = projected_data_B
  else:
    raise ValueError("Invalid covariate shift algorithm: {0} ".format(shift_alg))

  indexes = range(min(200,projected_data_A.shape[0])); numpy.random.shuffle(indexes); #Selecting 10 random samples for ploting
  for a in range(10):
    i = indexes[a]
    a = (projected_data_A[i,0], projected_data_A[i,1])
    #import ipdb; ipdb.set_trace();
    if len(shift.shape)== 1:
      b = (projected_data_A[i,0] + shift[0], projected_data_A[i,1] + shift[1])
    else:
      b = shift[i,:]
    
    ax.arrow(a[0],a[1],(b[0]-a[0]),(b[1]-a[1]), head_width=0.3, head_length=0.3, linewidth=0.5, fc='k', ec='k')

  # PLOTING THE MEAN
  #mu_A = numpy.mean(projected_dataA, axis=0)
  #mu_B = numpy.mean(projected_dataB, axis=0)
  #ax.arrow(mu_A[0],mu_A[1],(mu_B[0]-mu_A[0]),(mu_B[1]-mu_A[1]), head_width=5., head_length=5., linewidth="5.5",linestyle='dashdot', fc='b', ec='b')  
  
  #ax.text(mu_A[0],mu_A[1], "$\mu_A$")
  #ax.text(mu_B[0],mu_B[1], "$\mu_B$")  

  mpl.xlabel('$e_1$')
  mpl.ylabel('$e_2$')
  mpl.grid(True)
  
  
  mpl.legend(tuple(modalities))
  pp.savefig(fig)
  pp.close()


if __name__ == '__main__':
  main()
