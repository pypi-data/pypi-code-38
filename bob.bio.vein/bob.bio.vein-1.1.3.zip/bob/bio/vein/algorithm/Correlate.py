#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import numpy
import skimage.feature

from bob.bio.base.algorithm import Algorithm


class Correlate (Algorithm):
  """Correlate probe and model without cropping

  The method is based on "cross-correlation" between a model and a probe image.
  The difference between this and :py:class:`MiuraMatch` is that **no**
  cropping takes place on this implementation. We simply fill the excess
  boundary with zeros and extract the valid correlation region between the
  probe and the model using :py:func:`skimage.feature.match_template`.

  """

  def __init__(self):

    # call base class constructor
    Algorithm.__init__(
        self,
        multiple_model_scoring = None,
        multiple_probe_scoring = None
    )


  def enroll(self, enroll_features):
    """Enrolls the model by computing an average graph for each model"""

    # return the generated model
    return numpy.array(enroll_features)


  def score(self, model, probe):
    """Computes the score between the probe and the model.

    Parameters:

      model (numpy.ndarray): The model of the user to test the probe agains

      probe (numpy.ndarray): The probe to test


    Returns:

      float: Value between 0 and 0.5, larger value means a better match

    """

    I=probe.astype(numpy.float64)

    if len(model.shape) == 2:
      model = numpy.array([model])

    scores = []

    # iterate over all models for a given individual
    for md in model:

      R = md.astype(numpy.float64)
      Nm = skimage.feature.match_template(I, R)

      # figures out where the maximum is on the resulting matrix
      t0, s0 = numpy.unravel_index(Nm.argmax(), Nm.shape)

      # this is our output
      scores.append(Nm[t0,s0])

    return numpy.mean(scores)
