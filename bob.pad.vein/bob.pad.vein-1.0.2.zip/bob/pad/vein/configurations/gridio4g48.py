#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


'''Grid configurations for bob.pad.vein'''


import bob.bio.base

grid = bob.bio.base.grid.Grid(
    number_of_preprocessing_jobs = 48,
    number_of_extraction_jobs    = 48,
    number_of_projection_jobs    = 48,
    number_of_enrollment_jobs    = 48,
    number_of_scoring_jobs       = 48,
    training_queue               = '4G-io-big',
    preprocessing_queue          = '4G-io-big',
    extraction_queue             = '4G-io-big',
    projection_queue             = '4G-io-big',
    enrollment_queue             = '4G-io-big',
    scoring_queue                = '4G-io-big'
    )
'''Defines an SGE grid configuration for running at Idiap

This grid configuration will use 48 slots for each of the stages defined below.

The queue ``4G-io-big`` corresponds to the following settings:

  * ``queue``: ``q1d`` (in this queue you have a maximum of 48 slots according
    to: https://secure.idiap.ch/intranet/system/computing/ComputationGrid
  * ``memfree``: ``4G`` (this is the minimum amount of memory you can take -
    the lower, the more probable your job will be allocated faster)
  * ``io_big``: SET (this flag must be set so your job runs downstairs and not
    on people's workstations

Notice the queue names do not directly correspond SGE grid queue names. These
are names only known to :py:mod:`bob.bio.base.grid` and are translated
from there to settings which are finally passed to ``gridtk``.

To use this configuration file, just add it to your ``verify.py`` commandline.

For example::

  $ verify.py <other-options> gridio4g48

'''
