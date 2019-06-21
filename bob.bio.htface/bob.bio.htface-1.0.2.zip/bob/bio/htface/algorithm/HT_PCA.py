#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.learn.linear
import bob.io.base

import numpy
import scipy.spatial
from bob.bio.base import utils

import logging
logger = logging.getLogger("bob.bio.htface")

from .HTAlgorithm import HTAlgorithm


class HT_PCA (HTAlgorithm):
  """
  Eigenfaces with dataset shift from image modality A and B.
  
  Given X_A and X_B features from modality A and B, this algorithm tries to make P(X_A) = P(X_B) by doing znorm using only features from A.
    
  """

  def __init__(
      self,
      subspace_dimension,  # if int, number of subspace dimensions; if float, percentage of variance to keep
      distance_function = scipy.spatial.distance.euclidean,
      is_distance_function = True,
      **kwargs  # parameters directly sent to the base class
  ):

    HTAlgorithm.__init__(self,
        performs_projection = True, # enable if your tool will project the features
        requires_projector_training = True, # by default, the projector needs training, if projection is enabled
        split_training_features_by_client = False, # enable if your projector training needs the training files sorted by client
        split_training_features_by_modality = True, # enable if your projector training needs the training files sorted by modality      
        use_projected_features_for_enrollment = True, # by default, the enroller used projected features for enrollment, if projection is enabled.
        requires_enroller_training = False, # enable if your enroller needs training

        subspace_dimension = subspace_dimension,
        distance_function = distance_function,
        is_distance_function = is_distance_function,
        **kwargs
    )

    self.m_subspace_dim = subspace_dimension
    self.m_machine = None
    self.m_distance_function = distance_function
    self.m_factor = -1. if is_distance_function else 1.

    self.m_variances = None
    self.m_ht_offset = None
    self.m_ht_std    = None


  def train_projector(self, training_features, projector_file):
    """Generates the PCA covariance matrix"""

    # Initializes the data
    data_A = numpy.vstack([feature.flatten() for feature in training_features[0]])
    data_B = numpy.vstack([feature.flatten() for feature in training_features[1]])

    # Computing statistics from A
    data_A, mu_A, std_A = self._znorm(data_A)
    
    # Normalizing B with data from A
    data_B = (data_B - mu_A) / std_A    
    data = numpy.concatenate((data_A,data_B),axis=0)

    logger.info("  -> Training LinearMachine using PCA")
    t = bob.learn.linear.PCATrainer()
    self.m_machine, self.m_variances = t.train(data)
    self.m_machine.input_subtract = mu_A
    self.m_machine.input_divide = std_A

    # For re-shaping, we need to copy...
    self.variances = self.m_variances.copy()

    # compute variance percentage, if desired
    if isinstance(self.m_subspace_dim, float):
      cummulated = numpy.cumsum(self.m_variances) / numpy.sum(self.m_variances)
      for index in range(len(cummulated)):
        if cummulated[index] > self.m_subspace_dim:
          self.m_subspace_dim = index
          break
      self.m_subspace_dim = index
    logger.info("    ... Keeping %d PCA dimensions", self.m_subspace_dim)

    # re-shape machine
    self.m_machine.resize(self.m_machine.shape[0], self.m_subspace_dim)
    
    f = bob.io.base.HDF5File(projector_file, "w")    
    self.m_machine.save(f)


  def _znorm(self, data):
    """
    Z-Normalize
    """

    mu  = numpy.average(data,axis=0)
    std = numpy.std(data,axis=0)

    data = (data-mu)/std

    return data,mu,std

  """
  def compute_offset(self, data_A, data_B):
  
    projected_A = self.m_machine(data_A)
    projected_B = self.m_machine(data_B) 
  
    #mean shift
    offset = numpy.mean(projected_A, axis=0) - numpy.mean(projected_B, axis=0)
    
    #std of the modality A
    std = numpy.std(projected_A, axis=0)
    
    return offset, std
  """



  def load_projector(self, projector_file):
    """Reads the PCA projection matrix from file"""
    # read PCA projector
    f = bob.io.base.HDF5File(projector_file)
    #self.m_variances = f.read("Eigenvalues")
    #self.m_ht_offset = f.read("ht_offset")
    #self.m_ht_std    = f.read("ht_std")
    #f.cd("/Machine")
    self.m_machine = bob.learn.linear.Machine(f)
    # Allocates an array for the projected data
    #self.m_projected_feature = numpy.ndarray(self.m_machine.shape[1], numpy.float64)

  def project(self, feature):
    """Projects the data using the stored covariance matrix"""
    # return the projected data
    return self.m_machine(feature)

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
    """Computes the distance of the model to the probe using the distance function taken 
       from the config file applying from the feature offset
    """
    # return the negative distance (as a similarity measure)
    if len(model.shape) == 2:
      # we have multiple models, so we use the multiple model scoring
      return self.score_for_multiple_models(model, (probe))
    else:
      # single model, single probe (multiple probes have already been handled)
      return self.m_factor * self.m_distance_function(model, (probe))
