#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tue 27 Sep 2016 16:48:32 CEST

'''Maximum Curvature and Miura Matching baseline

References:

1. [MNM05]_
2. [TV13]_
3. [TVM14]_

'''

sub_directory = 'mc'
"""Sub-directory where results will be placed.

You may change this setting using the ``--sub-directory`` command-line option
or the attribute ``sub_directory`` in a configuration file loaded **after**
this resource.
"""

from ..preprocessor import NoCrop, TomesLeeMask, HuangNormalization, \
    NoFilter, Preprocessor

preprocessor = Preprocessor(
    crop=NoCrop(),
    mask=TomesLeeMask(),
    normalize=HuangNormalization(),
    filter=NoFilter(),
    )
"""Preprocessing using gray-level based finger cropping and no post-processing
"""

from ..extractor import MaximumCurvature
extractor = MaximumCurvature()
"""Features are the output of the maximum curvature algorithm, as described on
[MNM05]_.

Defaults taken from [TV13]_.
"""

# Notice the values of ch and cw are different than those from the
# repeated-line tracking baseline.
from ..algorithm import MiuraMatch
algorithm = MiuraMatch()
"""Miura-matching algorithm with specific settings for search displacement

Defaults taken from [TV13]_.
"""
