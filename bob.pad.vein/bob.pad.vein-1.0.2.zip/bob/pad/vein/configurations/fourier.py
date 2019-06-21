#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tue 27 Sep 2016 16:48:32 CEST

'''Fourier Transform baseline

Reference: [TREA15]_

'''

sub_directory = 'fourier'
"""Sub-directory where results will be placed.

You may change this setting using the ``--sub-directory`` command-line option
or the attribute ``sub_directory`` in a configuration file loaded **after**
this resource.
"""

from ..preprocessor import HistogramEqualization

preprocessor = HistogramEqualization()
"""Preprocessing using histogram equalization
"""

from ..extractor import FourierFeatures
extractor = FourierFeatures()
"""Features are the output of our custom FFT feature extractor, as described on
[TREA15]_.
"""

# Notice the values of ch and cw are different than those from the
# repeated-line tracking baseline.
from ..algorithm import NOOP
algorithm = NOOP()
"""Algorithm that does not nothing but to report its input.

Features from the extractor are already discriminative enough.
"""
