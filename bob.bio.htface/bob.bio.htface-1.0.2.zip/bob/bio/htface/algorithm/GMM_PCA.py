#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <Manuel.Guenther@idiap.ch>


import bob.core
import bob.io.base
import bob.learn.em

import numpy

#from bob.bio.base.algorithm import Algorithm
from bob.bio.gmm.algorithm import GMM

import logging
logger = logging.getLogger("bob.bio.gmm")

class GMM_PCA (GMM):
  """Algorithm for computing Universal Background Models and Gaussian Mixture Models of the features.
  Features must be normalized to zero mean and unit standard deviation.
  
  Before the  GMM training features are PCA projected
  
  """

  def __init__(
      self,
      # parameters for the GMM
      number_of_gaussians,

      subspace_dimension_pca = 0.9,
      # parameters of UBM training
      kmeans_training_iterations = 25,   # Maximum number of iterations for K-Means
      gmm_training_iterations = 25,      # Maximum number of iterations for ML GMM Training
      training_threshold = 5e-4,         # Threshold to end the ML training
      variance_threshold = 5e-4,         # Minimum value that a variance can reach
      update_weights = True,
      update_means = True,
      update_variances = True,
      # parameters of the GMM enrollment
      relevance_factor = 4,         # Relevance factor as described in Reynolds paper
      gmm_enroll_iterations = 1,    # Number of iterations for the enrollment phase
      responsibility_threshold = 0, # If set, the weight of a particular Gaussian will at least be greater than this threshold. In the case the real weight is lower, the prior mean value will be used to estimate the current mean and variance.
      INIT_SEED = 5489,
      # scoring
      scoring_function = bob.learn.em.linear_scoring
      
      
  ):
    """Initializes the local UBM-GMM tool chain with the given file selector object"""

    # call base class constructor and register that this tool performs projection
    GMM.__init__(
        self,
        number_of_gaussians = number_of_gaussians,
        kmeans_training_iterations = kmeans_training_iterations,
        gmm_training_iterations = gmm_training_iterations,
        training_threshold = training_threshold,
        variance_threshold = variance_threshold,
        update_weights = update_weights,
        update_means = update_means,
        update_variances = update_variances,
        relevance_factor = relevance_factor,
        gmm_enroll_iterations = gmm_enroll_iterations,
        responsibility_threshold = responsibility_threshold,
        INIT_SEED = INIT_SEED,
        scoring_function = scoring_function,

    )

    self.subspace_dimension_pca = subspace_dimension_pca
    self.pca_machine = None
    

  def _check_feature(self, feature):
    """Checks that the features are appropriate"""
    if not isinstance(feature, numpy.ndarray) or feature.ndim != 2 or feature.dtype != numpy.float64:
      raise ValueError("The given feature is not appropriate")
    if self.ubm is not None and feature.shape[1] != self.pca_machine.shape[0]:
      raise ValueError("The given feature is expected to have %d elements, but it has %d" % (self.ubm.shape[1], feature.shape[1]))

  ##############################
  ############ PCA #############

  def train_pca(self, data):
    """Trains and returns a LinearMachine that is trained using PCA"""

    logger.info("  -> Training LinearMachine using PCA ")
    trainer = bob.learn.linear.PCATrainer()
    machine, eigen_values = trainer.train(data)

    if isinstance(self.subspace_dimension_pca, float):
      cummulated = numpy.cumsum(eigen_values) / numpy.sum(eigen_values)
      for index in range(len(cummulated)):
        if cummulated[index] > self.subspace_dimension_pca:
          self.subspace_dimension_pca = index
          break
      self.subspace_dimension_pca = index

    # limit number of pcs
    logger.info("  -> limiting PCA subspace to %d dimensions", self.subspace_dimension_pca)
    machine.resize(machine.shape[0], self.subspace_dimension_pca)
    
    self.pca_machine = machine

  def perform_pca(self, training_set):
    """Perform PCA on data"""
    return self.pca_machine(training_set)

  def save_pca(self, hdf5):
    hdf5.create_group('/pca')
    hdf5.cd('/pca')
    self.pca_machine.save(hdf5)
    hdf5.cd('..')

  def load_pca(self, hdf5_file):
    hdf5 = bob.io.base.HDF5File(hdf5_file)
    if hdf5.has_group("/pca"):
      hdf5.cd('/pca')
      self.pca_machine = bob.learn.linear.Machine(hdf5)


  def train_projector(self, train_features, projector_file):
    """Computes the Universal Background Model from the training ("world") data"""
    [self._check_feature(feature) for feature in train_features]

    logger.info("  -> Training UBM model with %d training files", len(train_features))

    # Loads the data into an array
    array = numpy.vstack(train_features)
    
    self.train_pca(array)
    
    self.train_ubm(self.perform_pca(array))

    hdf5 = bob.io.base.HDF5File(projector_file, 'w')    

    self.save_pca(hdf5)

    self.save_ubm(hdf5)
    

  #######################################################
  ############## GMM training using UBM + PCA #################

  def load_projector(self, projector_file):
    """Reads the UBM model from file"""

    # read PCA
    self.load_pca(projector_file)

    # read UBM    
    self.load_ubm(projector_file)

    # prepare MAP_GMM_Trainer
    kwargs = dict(mean_var_update_responsibilities_threshold=self.responsibility_threshold) if self.responsibility_threshold > 0. else dict()
    self.enroll_trainer = bob.learn.em.MAP_GMMTrainer(self.ubm, relevance_factor = self.relevance_factor, update_means = True, update_variances = False, **kwargs)
    self.rng = bob.core.random.mt19937(self.init_seed)

  def project_ubm(self, array):
  
    logger.debug(" .... Projecting %d feature vectors" % array.shape[0])
    # Accumulates statistics
    gmm_stats = bob.learn.em.GMMStats(self.ubm.shape[0], self.ubm.shape[1])
    self.ubm.acc_statistics(array, gmm_stats)

    # return the resulting statistics
    return gmm_stats

  def project(self, feature):
    """Computes GMM statistics against a UBM, given an input 2D numpy.ndarray of feature vectors"""
    self._check_feature(feature)

    return self.project_ubm(self.perform_pca(feature))

  def enroll(self, feature_arrays):
    """Enrolls a GMM using MAP adaptation, given a list of 2D numpy.ndarray's of feature vectors"""
    [self._check_feature(feature) for feature in feature_arrays]
    array = numpy.vstack(feature_arrays)
    # Use the array to train a GMM and return it
    return self.enroll_gmm(self.perform_pca(array))

