#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Wed 19 Oct 23:43:22 2016

import bob.io.base

import numpy

import bob.learn.linear

from bob.pad.base.algorithm import Algorithm

import logging

logger = logging.getLogger("bob.pad.voice")


class LogRegr(Algorithm):
    """Trains Logistical Regression classifier and projects testing dat on it."""

    def __init__(self, use_PCA_training=False, normalize_features=False, **kwargs):

        # call base class constructor registering that this tool performs everything.
        Algorithm.__init__(
            self,
            performs_projection=True,
            requires_projector_training=True,
            use_projected_features_for_enrollment=True,
        )
        self.machine = None
        self.pca_machine = None
        self.use_PCA_training = use_PCA_training
        self.normalize_features = normalize_features

    def _check_feature(self, feature, machine=None, projected=False):
        """Checks that the features are appropriate."""
        if not isinstance(feature, numpy.ndarray) or feature.ndim != 1 or feature.dtype != numpy.float64:
            raise ValueError("The given feature is not appropriate", feature)
        index = 1 if projected else 0
        if machine is not None and feature.shape[0] != machine.shape[index]:
            logger.warn("The given feature is expected to have %d elements, but it has %d" % (
            machine.shape[index], feature.shape[0]))
            return False
        return True

    def train_projector(self, training_features, projector_file):
        if len(training_features) < 2:
            raise ValueError("Training projector: features should contain two lists: real and attack!")

        # the format is specified in FileSelector.py:training_list() of bob.spoof.base

        logger.info(" - Training: number of real features %d", len(training_features[0]))
        # print (training_features[0])
        if isinstance(training_features[0][0][0], numpy.ndarray):
            logger.info(" - Training: each feature is a set of arrays")
            real_features = numpy.array(
                [row if self._check_feature(row) else numpy.nan for feat in training_features[0] for row in feat],
                dtype=numpy.float64)
            attack_features = numpy.array(
                [row if self._check_feature(row) else numpy.nan for feat in training_features[1] for row in feat],
                dtype=numpy.float64)
        else:
            logger.info(" - Training: each feature is a single array")
            real_features = numpy.array(
                [feat if self._check_feature(feat) else numpy.nan for feat in training_features[0]],
                dtype=numpy.float64)
            attack_features = numpy.array(
                [feat if self._check_feature(feat) else numpy.nan for feat in training_features[1]],
                dtype=numpy.float64)

        # print ("LogRegr:train_projector(), real_features shape:", real_features.shape)
        # print ("LogRegr:train_projector(), attack_features shape:", attack_features.shape)
        # print ("Min real ", numpy.min(real_features))
        # print ("Max real ", numpy.max(real_features))
        # print ("Min attack ", numpy.min(attack_features))
        # print ("Max attack ", numpy.max(attack_features))

        # save the trained model to file for future use
        hdf5file = bob.io.base.HDF5File(projector_file, "w")

        from bob.pad.voice.utils import extraction

        mean = None
        std = None
        # reduce the feature space using PCA
        if self.use_PCA_training or self.normalize_features:
            mean, std = extraction.calc_mean_std(real_features, attack_features, nonStdZero=True)
            real_features = extraction.zeromean_unitvar_norm(real_features, mean, std)
            attack_features = extraction.zeromean_unitvar_norm(attack_features, mean, std)

        if self.use_PCA_training:
            pca_trainer = bob.learn.linear.PCATrainer()
            self.pca_machine, eigenvalues = pca_trainer.train(numpy.vstack((real_features, attack_features)))

            # select only meaningful weights
            cummulated = numpy.cumsum(eigenvalues) / numpy.sum(eigenvalues)
            for index in range(len(cummulated)):
                if cummulated[index] > 0.99:  # variance
                    subspace_dimension = index
                    break
            subspace_dimension = index

            # save the PCA matrix
            self.pca_machine.resize(self.pca_machine.shape[0], subspace_dimension)
            if mean is not None and std is not None:
                self.pca_machine.input_subtract = mean
                self.pca_machine.input_divide = std

            hdf5file.create_group('PCAProjector')
            hdf5file.cd('PCAProjector')
            self.pca_machine.save(hdf5file)

            # project all current features on PCA
            real_features = [self.pca_machine(feature) for feature in real_features]
            real_features = numpy.asarray(real_features, dtype=numpy.float64)
            attack_features = [self.pca_machine(feature) for feature in attack_features]
            attack_features = numpy.asarray(attack_features, dtype=numpy.float64)

        # create Logistic Regression Machine
        trainer = bob.learn.linear.CGLogRegTrainer()

        # train the mchine using the provided training data
        # negative features go first, positive - second
        self.machine = trainer.train(attack_features, real_features)

        # if we use PCA, PCA machine is normalizing features already
        if self.normalize_features and not self.use_PCA_training:
            if mean is not None and std is not None:
                self.machine.input_subtract = mean
                self.machine.input_divide = std

        # print ("LogRegr:train_projector(), machine shape: ", self.machine.shape)
        # print ("LogRegr:train_projector(), machine weights: ", self.machine.weights)

        hdf5file.cd('/')
        hdf5file.create_group('LogRegProjector')
        hdf5file.cd('LogRegProjector')
        self.machine.save(hdf5file)

    def load_projector(self, projector_file):
        hdf5file = bob.io.base.HDF5File(projector_file)

        if self.use_PCA_training:
            hdf5file.cd('/PCAProjector')
            self.pca_machine = bob.learn.linear.Machine(hdf5file)

        # read LogRegr Machine model
        hdf5file.cd('/LogRegProjector')
        self.machine = bob.learn.linear.Machine(hdf5file)

    def project_feature(self, feature):

        feature = numpy.asarray(feature, dtype=numpy.float64)

        # reduce dimension using PCA
        if self.use_PCA_training and self._check_feature(feature, machine=self.pca_machine):
            feature = self.pca_machine(feature)

        if self._check_feature(feature, machine=self.machine):
            # Projects the data on LogRegression classifier
            projection = self.machine(feature)
            return projection
        return numpy.zeros(1, dtype=numpy.float64)

    def project(self, feature):
        """project(feature) -> projected

        Projects the given feature into Fisher space.

        **Parameters:**

        feature : 1D :py:class:`numpy.ndarray`
          The 1D feature to be projected.

        **Returns:**

        projected : 1D :py:class:`numpy.ndarray`
          The ``feature`` projected into Fisher space.
        """

        if len(feature) > 0:
            if isinstance(feature[0], numpy.ndarray) or isinstance(feature[0], list):
                return [self.project_feature(feat) for feat in feature]
            else:
                return self.project_feature(feature)
        else:
            return numpy.zeros(1, dtype=numpy.float64)

    def enroll(self, enroll_features):
        """We do no enrollment here"""
        assert len(enroll_features)
        # we need no enrollment
        return enroll_features

    def score(self, toscore):
        """Returns the output of a classifier"""

        return toscore

    def score_for_multiple_projections(self, toscore):

        return toscore


algorithm = LogRegr()
