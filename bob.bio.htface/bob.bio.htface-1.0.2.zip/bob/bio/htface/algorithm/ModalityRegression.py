#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.learn.linear
import bob.io.base
import numpy
import scipy.spatial

import logging
logger = logging.getLogger("bob.bio.htface")

from .HTAlgorithm import HTAlgorithm


class GFK (HTAlgorithm):
  """
  Basically we learn a linear regressor from modality A to modality B    
  """

  def __init__(
      self,
      distance_function = scipy.spatial.distance.euclidean,
      is_distance_function = True,
      uses_variances = False,
      use_pinv=True,
      **kwargs  # parameters directly sent to the base class
  ):


    # call base class constructor and register that the algorithm performs a projection
    HTAlgorithm.__init__(self,
        performs_projection = False, # enable if your tool will project the features
        requires_projector_training = True, # by default, the projector needs training, if projection is enabled
        split_training_features_by_client = False, # enable if your projector training needs the training files sorted by client
        split_training_features_by_modality = True, # enable if your projector training needs the training files sorted by modality      
        use_projected_features_for_enrollment = False, # by default, the enroller used projected features for enrollment, if projection is enabled.
        requires_enroller_training = False, # enable if your enroller needs training

        subspace_dimension = subspace_dimension,
        distance_function = distance_function,
        is_distance_function = is_distance_function,
        **kwargs
    )

    self.m_distance_function = distance_function
    self.m_factor = -1. if is_distance_function else 1.
    self.m_principal_angles_dimension = principal_angles_dimension
    self.requires_projector_training = True


  def train_projector(self, training_features, projector_file):
    """Compute the kernel"""

    source = training_features[0]
    target = training_features[1]
    source = source.astype("float64")
    target = target.astype("float64")    

        
    
    del f

  def load_projector(self, projector_file):
    """Reads the PCA projection matrix from file"""
    # read PCA projector
    f = bob.io.base.HDF5File(projector_file, 'r')
    f.cd("/source_machine")
    self.source_machine = bob.learn.linear.Machine(f)
    f.cd("..")
    f.cd("/target_machine")
    self.target_machine = bob.learn.linear.Machine(f)
    f.cd("..")
    self.G = f.get("G")
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
    model = (model-self.source_machine.input_subtract) / self.source_machine.input_divide
    probe = (probe-self.target_machine.input_subtract) / self.target_machine.input_divide
    
    return numpy.dot(numpy.dot(model,self.G), probe.T)[0]

    #return numpy.dot(numpy.dot(model,self.G), probe.T)[0]

