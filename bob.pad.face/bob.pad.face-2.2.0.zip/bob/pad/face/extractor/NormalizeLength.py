#!/usr/bin/env python
# encoding: utf-8

import numpy

from bob.bio.base.extractor import Extractor

import logging
logger = logging.getLogger("bob.pad.face")


class NormalizeLength(Extractor, object):
  """
  Normalize the length of feature vectors, such that 
  they all have the same dimensions

  **Parameters:**

  length: int
    The final length of the final feature vector 

  requires_training: boolean
    This extractor actually may requires "training".
    The goal here is to retrieve the length of the shortest sequence

  debug: boolean
    Plot stuff
  """
  def __init__(self, length=-1, debug=False, requires_training=True, **kwargs):

    super(NormalizeLength, self).__init__(requires_training=requires_training, **kwargs)
    
    self.length = length
    self.debug = debug

  def __call__(self, signal):
    """
    Normalize the length of the signal 

    **Parameters:**

    signal: numpy.array 
      The signal

    **Returns:**

      signal: numpy.array 
       the signal with the provided length 
    """
    # we have a single pulse signal
    if signal.ndim == 1:
      signal = signal[:self.length]

    # we have 3 pulse signal (Li's preprocessing)
    # in this case, return the signal corresponding to the green channel
    if signal.ndim == 2 and (signal.shape[1] == 3):
      signal = signal[:self.length, 1]
    
    if numpy.isnan(numpy.sum(signal)):
      return

    if signal.shape[0] < self.length:
      logger.debug("signal shorter than training shape: {} vs {}".format(signal.shape[0], self.length))
      import sys
      sys.exit()
      tmp = numpy.zeros((self.length), dtype=signal.dtype)
      tmp[:, signal.shape[0]]
      signal = tmp

    if self.debug: 
      from matplotlib import pyplot
      pyplot.plot(signal, 'k')
      pyplot.title('Signal truncated')
      pyplot.show()

    return signal

  def train(self, training_data, extractor_file):
    """
    This function determines the shortest length across the training set.
    It will be used to normalize the length of all the sequences.

    **Parameters:**

    training_data : [object] or [[object]]
      A list of *preprocessed* data that can be used for training the extractor.
      Data will be provided in a single list, if ``split_training_features_by_client = False`` was specified in the constructor,
      otherwise the data will be split into lists, each of which contains the data of a single (training-)client.

    extractor_file : str
      The file to write.
      This file should be readable with the :py:meth:`load` function.
    """
    self.length = 100000 
    for i in range(len(training_data)):
      if training_data[i].shape[0] < self.length:
        self.length = training_data[i].shape[0]
    logger.info("Signals will be truncated to {} dimensions".format(self.length))
