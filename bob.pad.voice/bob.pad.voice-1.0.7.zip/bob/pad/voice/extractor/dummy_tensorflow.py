#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Tue 15 Nov 15:43:22 CEST 2016

from bob.bio.base.extractor import Extractor
from bob.bio.spear.preprocessor import Base

import numpy

import logging

logger = logging.getLogger("bob.pad.voice")


class DummyTF(Base, Extractor):
    """
    This class can be used as a simple preprocessor (reads data only) and a dummy extractor (reads saved data)
    """
    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        Extractor.__init__(self, requires_training=False, split_training_data_by_client=False, **kwargs)

    def __call__(self, input_data, annotations):
        """
        We assume here that this will be called only once in the capacity of Preprocessor.
        If it is called as an Extractor, it will break. To avoid it, make sure path to preprocessing directory
        and extraction directory are the same. It will ensure that both preprocessing and extraction files are
        exactly the same, and this called will be executed only the first time (when preprocessing)
        """
        # create empty labels array, since this what read/write function of Base accepts
        labels = numpy.ones(len(input_data[1]))
        return input_data[0], input_data[1], labels


dummytf = DummyTF()
