#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Thu Apr 21 16:41:21 CEST 2016
#

from bob.bio.base.extractor import Extractor

_data = [0., 1., 2., 3., 4., 5., 6.]


class DummyExtractor(Extractor):
    def __init__(self, **kwargs):
        Extractor.__init__(self, requires_training=True)

    def __call__(self, data):
        """Does nothing, simply converts the data type of the data."""
        assert (data in _data)
        return data + 1.0

    def train(self, training_data, extractor_file):
        pass

extractor = DummyExtractor()
