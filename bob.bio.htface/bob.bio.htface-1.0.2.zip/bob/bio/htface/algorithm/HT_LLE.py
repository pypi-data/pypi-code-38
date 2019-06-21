#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.learn.linear
import bob.io.base

import numpy
import scipy.spatial

import sklearn.manifold

import logging
logger = logging.getLogger("bob.bio.htface")

from .HTAlgorithm import HTAlgorithm


class HT_LLE (HTAlgorithm):
  """Tool for computing LLE shift"""

  def __init__(
      self,
      subspace_dimension,  # if int, number of subspace dimensions in the end
      n_neighbors, #Number of neighbors for reconstruction 
      scikit_lle_version='standard',#[standard | hessian | modified | ltsa]
      distance_function = scipy.spatial.distance.euclidean,
      is_distance_function = True,
      do_shift=False,
      uses_variances = False,

      **kwargs  # parameters directly sent to the base class
  ):

    # call base class constructor and register that the algorithm performs a projection
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
    self.m_n_neighbors  = n_neighbors
    self.m_machine = None
    self.m_distance_function = distance_function
    self.m_factor = -1. if is_distance_function else 1.
    self.m_uses_variances = uses_variances
    self.m_scikit_lle_version = scikit_lle_version
    self.do_shift = do_shift


  def train_projector(self, training_features, projector_file):
    """Generates the PCA covariance matrix"""
        
    # Initializes the data
    data_A = numpy.vstack([feature.flatten() for feature in training_features[0]])
    data_B = numpy.vstack([feature.flatten() for feature in training_features[1]])
    data = numpy.concatenate((data_A,data_B),axis=0)

    logger.info("  -> Training LLE reducing to dimension {0} and using {1} components for the reconstruction".format(self.m_subspace_dim, self.m_n_neighbors))

    self.m_machine = sklearn.manifold.LocallyLinearEmbedding(n_neighbors=self.m_n_neighbors, n_components=self.m_subspace_dim, method=self.m_scikit_lle_version)
    self.m_machine.fit(data)

    #Saving the offsets
    if self.do_shift:
      self.m_ht_offset, self.m_ht_std = self.compute_offset(data_A, data_B)
    else:    
      self.m_ht_offset = 0
      self.m_ht_std = 0

    f = bob.io.base.HDF5File(projector_file, "w")
    f.set("ht_offset", self.m_ht_offset)
    f.set("ht_std", self.m_ht_std)
    del f

    #Saving the LLE
    from sklearn.externals import joblib
    joblib.dump(self.m_machine, projector_file + ".pickle")

  def compute_offset(self, data_A, data_B):
  
    projected_A = self.m_machine.transform(data_A)
    projected_B = self.m_machine.transform(data_B) 
  
    #mean shift
    offset = numpy.mean(projected_A, axis=0) - numpy.mean(projected_B, axis=0)
    
    #std of the modality A
    std = numpy.std(projected_A, axis=0)
    
    return offset, std



  def load_projector(self, projector_file):
    """Reads the PCA projection matrix from file"""
    # read PCA projector
    f = bob.io.base.HDF5File(projector_file)
    self.m_ht_offset = f.read("ht_offset")
    self.m_ht_std    = f.read("ht_std")
    del f

    from sklearn.externals import joblib
    self.m_machine = joblib.load(projector_file + ".pickle") 


  def project(self, feature):
    """Projects the data using the stored covariance matrix"""
    # return the projected data
    return self.m_machine.transform(feature)[0,:]


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
    """Computes the distance of the model to the probe using the distance function taken from the config file
    
    PLUS
    
    HT OFFSET
    
    """
    # return the negative distance (as a similarity measure)
    if len(model.shape) == 2:
      # we have multiple models, so we use the multiple model scoring
      return self.score_for_multiple_models(model, (probe + self.m_ht_offset))
    elif self.m_uses_variances:
      # single model, single probe (multiple probes have already been handled)
      return self.m_factor * self.m_distance_function(model, (probe + self.m_ht_offset), self.m_variances)
    else:
      # single model, single probe (multiple probes have already been handled)
      return self.m_factor * self.m_distance_function(model, (probe + self.m_ht_offset))
