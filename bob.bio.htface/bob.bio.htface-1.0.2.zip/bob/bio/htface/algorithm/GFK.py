#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.learn.linear
import bob.io.base
import numpy
import scipy.spatial
import bob.bio.base

import logging
logger = logging.getLogger("bob.bio.htface")

from bob.learn.linear import GFKMachine, GFKTrainer


class GFK (bob.bio.base.algorithm.Algorithm):
  """
  
  Implementing the algorithm Geodesic Flow Kernel to do transfer learning from the modality A to modality B from the paper
  
  Gong, Boqing, et al. "Geodesic flow kernel for unsupervised domain adaptation." Computer Vision and Pattern Recognition (CVPR), 2012 IEEE Conference on. IEEE, 2012.  
  
  
  A very good explanation can be found here
  
  http://www-scf.usc.edu/~boqinggo/domainadaptation.html#gfk_section
  
  """

  def __init__(
      self,
      number_of_subspaces,  # if int, number of subspace dimensions; if float, percentage of variance to keep
      source_subspace_dimension,
      target_subspace_dimension,      
      use_lda=False, # BUild the subspaces with LDA
      distance_function = scipy.spatial.distance.euclidean,
      is_distance_function = True,
      uses_variances = False,
      use_pinv=True,
      **kwargs  # parameters directly sent to the base class
  ):

      split_training_features_by_client = False
      if use_lda:
          split_training_features_by_client = True   

       # call base class constructor and register that the algorithm performs a projection
      bob.bio.base.algorithm.Algorithm.__init__(self,
            performs_projection = False, # enable if your tool will project the features
            requires_projector_training = True, # by default, the projector needs training, if projection is enabled
            split_training_features_by_client = split_training_features_by_client, # enable if your projector training needs the training files sorted by client
            use_projected_features_for_enrollment = False, # by default, the enroller used projected features for enrollment, if projection is enabled.
            requires_enroller_training = False, # enable if your enroller needs training

            distance_function = distance_function,
            is_distance_function = is_distance_function,
            **kwargs
      )

      self.m_number_of_subspaces = number_of_subspaces
      self.m_source_subspace_dimension = source_subspace_dimension
      self.m_target_subspace_dimension = target_subspace_dimension
      self.gfk_machine = None

      self.m_distance_function = distance_function
      self.m_factor = -1. if is_distance_function else 1.
      self.m_uses_variances = uses_variances
      
      self.requires_projector_training = True
      self.eps = 1e-20;
      self.use_lda = use_lda


  def split_data_by_modality(self, data, metadata, split_training_features_by_client):
      source_jets = []
      target_jets = []
      if split_training_features_by_client:
          
          source_jets_tmp = []
          target_jets_tmp = []
          for client_data, client_metadata in zip(data, metadata):

              for d, m in zip(client_data, client_metadata):
                  if m.db.modality_separator == m.modality:
                      source_jets_tmp.append(d)
                  else:
                      target_jets_tmp.append(d)
          source_jets.append(source_jets_tmp)
          target_jets.append(target_jets_tmp)

      else:
          for d, m in zip(data, metadata):
              if m.db.modality_separator == m.modality:
                  source_jets.append(d)
              else:
                  target_jets.append(d)
  
      return source_jets, target_jets


  def train_projector(self, training_features, projector_file):
      """Compute the kernel"""

      gfk_trainer = GFKTrainer(self.m_number_of_subspaces, 
                               subspace_dim_source=self.self.m_source_subspace_dimension,
                               subspace_dim_target=self.m_target_subspace_dimension,
                               eps=self.eps)

      source_data = training_features[0]
      target_data = training_features[1]
      
      self.gfk_machine = gfk_trainer.train(source_data, target_data)
      self.save_projector(projector_file)
    

  def save_projector(self, projector_file):
      """Reads the1 PCA projection matrix from file"""
      # read PCA projector
      f = bob.io.base.HDF5File(projector_file, 'w')
      self.gfk_machine.save(f)
      del f


  def load_projector(self, projector_file):
      """Reads the1 PCA projection matrix from file"""
      # read PCA projector
      f = bob.io.base.HDF5File(projector_file, 'r')
      self.gfk_machine = GFKMachine(f)
      del f    


  def project(self, feature):
      """Projects the data using the stored covariance matrix"""
      raise NotImplemented("There is no projection")

  def enroll(self, enroll_features):
      """Enrolls the model by computing an average of the given input vectors"""
      assert len(enroll_features)
      # just store all the features
      model = numpy.zeros((len(enroll_features), enroll_features[0].shape[0]), numpy.float64)
      for n, feature in enumerate(enroll_features):
        model[n,:] += feature[:]

      # return enrolled model
      return model

  def score(self, model, probe):
      """Computes the distance of the model to the probe using the distance function taken from the config file"""
      return self.gfk_machine(model, probe)

