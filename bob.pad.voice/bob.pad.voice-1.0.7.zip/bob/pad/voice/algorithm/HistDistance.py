#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Wed 19 Oct 23:43:22 2016


import bob.io.base

import numpy
import math

import bob.learn.linear

from bob.pad.base.algorithm import Algorithm

import logging

logger = logging.getLogger("bob.pad.voice")


class HistDistance(Algorithm):
    """This class is used to test all the possible functions of the tool chain, but it does basically nothing."""

    def __init__(self, chi_square=False, hist_intersection=True, probab_dist=False, normalize_features=True, **kwargs):
        """Generates a test value that is read and written"""

        # call base class constructor registering that this tool performs everything.
        Algorithm.__init__(
            self,
            performs_projection=True,
            requires_projector_training=True,
            use_projected_features_for_enrollment=True,
        )
        self.real_mean = None
        self.attack_mean = None
        self.normalize_features = normalize_features
        self.hist_intersection = hist_intersection
        self.chi_square = chi_square
        self.probab_dist = probab_dist

    def _check_feature(self, feature, mean_hist=None):
        """Checks that the features are appropriate."""
        if not isinstance(feature, numpy.ndarray) or feature.ndim != 1 or feature.dtype != numpy.float64:
            raise ValueError("The given feature is not appropriate", feature)
        if mean_hist is not None and feature.shape[0] != mean_hist.shape[0]:
            logger.warn("The given feature is expected to have %d elements, but it has %d" % (
            mean_hist.shape[0], feature.shape[0]))
            return False
        return True

    def train_projector(self, training_features, projector_file):
        if len(training_features) < 2:
            raise ValueError("Training projector: features should contain two lists: real and attack!")

            # the format is specified in FileSelector.py:training_list() of bob.spoof.base
        #    print ("HistDistance:train_projector(), training_features", type(training_features[0][0]))

        if isinstance(training_features[0][0][0], numpy.ndarray):
            print ("HistDistance:train_projector(), features are set of arrays of length: ",
                   len(training_features[0][0][0]))
            real_features = numpy.array([row for feat in training_features[0] for row in feat], dtype=numpy.float64)
            attack_features = numpy.array([row for feat in training_features[1] for row in feat], dtype=numpy.float64)
        else:
            real_features = numpy.array(training_features[0], dtype=numpy.float64)
            attack_features = numpy.array(training_features[1], dtype=numpy.float64)

        # #    print ("HistDistance:train_projector(), real_features", real_features)
        # #    print ("HistDistance:train_projector(), attack_features", attack_features)
        # print ("HistDistance:train_projector(), real_features shape:", real_features.shape)
        # print ("HistDistance:train_projector(), attack_features shape:", attack_features.shape)
        # #    real_features[real_features<-1024] = -1024
        # #    attack_features[attack_features<-1024] = -1024
        # print ("Min real ", numpy.min(real_features))
        # print ("Max real ", numpy.max(real_features))
        # print ("Min attack ", numpy.min(attack_features))
        # print ("Max attack ", numpy.max(attack_features))

        from bob.pad.voice.utils import extraction

        mean = None
        std = None
        # normalize features column-wise
        if self.normalize_features:
            mean, std = extraction.calc_mean_std(real_features, attack_features, nonStdZero=True)
            real_features = extraction.zeromean_unitvar_norm(real_features, mean, std)
            attack_features = extraction.zeromean_unitvar_norm(attack_features, mean, std)

        # compute average histogram for each type of features
        self.real_mean = numpy.mean(real_features, axis=0)
        self.attack_mean = numpy.mean(attack_features, axis=0)

        # print ("shape of average real", self.real_mean.shape)
        # print ("(min, max) average real (%f, %f)" % (numpy.min(self.real_mean), numpy.max(self.real_mean)))
        # print ("shape of average attack", self.attack_mean.shape)
        # print ("(min, max) average attack (%f, %f)" % (numpy.min(self.attack_mean), numpy.max(self.attack_mean)))

        from bob.pad.base import utils

        # save the models to file for future use
        hdf5file = bob.io.base.HDF5File(projector_file, "w")
        hdf5file.set("AvHistReal", self.real_mean)
        hdf5file.set("AvHistAttackl", self.attack_mean)

    def load_projector(self, projector_file):
        hdf5file = bob.io.base.HDF5File(projector_file)

        self.real_mean = hdf5file.read("AvHistReal")
        self.attack_mean = hdf5file.read("AvHistAttackl")

    def hist_bin(self, hist, xi):
        if xi > hist.shape[0]:
            raise ValueError("The coordinate for bin value of histogram (size: %d) is %d, which is too large",
                             hist.shape[0], xi)
        return hist[xi]

    def project_feature(self, feature):

        feature = numpy.asarray(feature, dtype=numpy.float64)

        # here, features are lbp images, so they are different from the rest
        if self.probab_dist:
            if feature.shape[0]:  # not empty
                pprobab_real = numpy.sum([math.log(self.hist_bin(self.real_mean, xi)) for xi in feature])
                pprobab_attack = numpy.sum([math.log(self.hist_bin(self.attack_mean, xi)) for xi in feature])
                return numpy.array([pprobab_real - pprobab_attack], dtype=numpy.float64)

        if self._check_feature(feature, self.real_mean):

            import bob.math
            # Find the distance from the feature-histogram and the average models
            if self.chi_square:
                dist_real = bob.math.chi_square(self.real_mean, feature)
                dist_attack = bob.math.chi_square(self.attack_mean, feature)
            elif self.hist_intersection:
                dist_real = bob.math.histogram_intersection(self.real_mean, feature)
                dist_attack = bob.math.histogram_intersection(self.attack_mean, feature)
            else:
                raise ValueError("HistDistance: please specify the metric for histogram distance")

            #      print ("HistDistance:project(), projection: ", projection)
            return numpy.array([dist_real, dist_attack], dtype=numpy.float64)
            # return self.machine(feature)
        return numpy.zeros(2, dtype=numpy.float64)

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

        print ("HistDistance:project(), feature shape: ", feature.shape)

        if len(feature) > 0:
            if isinstance(feature[0], numpy.ndarray) or isinstance(feature[0], list):
                return [self.project_feature(feat) for feat in feature]
            else:
                return self.project_feature(feature)
        else:
            return numpy.zeros(1, dtype=numpy.float64)

    def score(self, toscore):
        """Returns the evarage value of the probe"""
        print("HistDistance:score() the score: ", toscore)

        # projection is already the score in this case
        if self.probab_dist:
            return toscore

        dist_real = toscore[0]
        dist_attack = toscore[1]

        if self.chi_square:
            # chi-square distance to attack is smaller if it is nearer the attack mean
            # so, attack features have negative scores and real - positive
            return [dist_attack - dist_real]
        elif self.hist_intersection:
            # the situation with histogram intersection metrics is reversed compared to chi-square
            # histogram intersection is similarity measure, the higher value the closeer it is
            # attack features have negative scores and real - positive scores
            return [dist_real - dist_attack]

        else:
            raise ValueError("HistDistance:scoring() please specify the metric for histogram distance")

    def score_for_multiple_projections(self, toscore):
        print("HistDistance:score_for_multiple_projections() the score: ", len(toscore))

        return numpy.array([self.score(score) for score in toscore], dtype=numpy.float64)


algorithm = HistDistance()
