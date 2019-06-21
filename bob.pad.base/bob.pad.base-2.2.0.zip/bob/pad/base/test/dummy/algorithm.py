#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Thu Apr 21 16:41:21 CEST 2016
#


import numpy
import bob.io.base

from bob.pad.base.algorithm import Algorithm

_data = [1., 2., 3., 4., 5., 6., 7.]


class DummyAlgorithm(Algorithm):
    """This class is used to test all the possible functions of the tool chain, but it does basically nothing."""

    def __init__(self, **kwargs):
        """Generates a test value that is read and written"""

        # call base class constructor registering that this tool performs everything.
        Algorithm.__init__(
            self,
            performs_projection=True,
            requires_enroller_training=True
        )

    def _test(self, file_name):
        """Simply tests that the read data is consistent"""
        data = bob.io.base.load(file_name)
        assert (_data == data[0]).any()

    def train_projector(self, training_features, projector_file):
        """Does not train the projector, but writes some file"""
        # save something
        bob.io.base.save(training_features, projector_file)

    def load_projector(self, projector_file):
        """Loads the test value from file and compares it with the desired one"""
        self._test(projector_file)

    def project(self, feature):
        """Just returns the feature since this dummy implementation does not really project the data"""
        return feature

    def score(self, probe):
        """Returns the Euclidean distance between model and probe"""
        return [numpy.mean(probe)]


algorithm = DummyAlgorithm()
