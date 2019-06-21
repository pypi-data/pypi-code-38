#!/usr/bin/env python
# encoding: utf-8

import numpy

from bob.bio.base.extractor import Extractor

from bob.core.log import setup
logger = setup("bob.pad.face")


class PPGSecure(Extractor, object):
  """Extract frequency spectra from pulse signals.
  
  The feature are extracted according to what is described in 
  the following article:

  E.M Nowara, A. Sabharwal and A. Veeraraghavan,
  "PPGSecure: Biometric Presentation Attack Detection using Photoplethysmograms",
  IEEE Intl Conf. on Automatic Face and Gesture Recognition, 2017.

  Attributes
  ----------
  framerate : :obj:`int`
    The sampling frequency of the signal (i.e the framerate ...) 
  nfft : :obj:`int`
    Number of points to compute the FFT
  debug : :obj:`bool`
    Plot stuff
  
  """
  def __init__(self, framerate=25, nfft=32, debug=False, **kwargs):
    """Init function

    Parameters
    ----------
    framerate : :obj:`int`
      The sampling frequency of the signal (i.e the framerate ...) 
    nfft : :obj:`int`
      Number of points to compute the FFT
    debug : :obj:`bool`
      Plot stuff
    
    """
    super(PPGSecure, self).__init__(**kwargs)
    self.framerate = framerate
    self.nfft = nfft
    self.debug = debug


  def __call__(self, signal):
    """Compute and concatenate frequency spectra for the given signals.

    Parameters
    ----------
    signal : :py:class:`numpy.ndarray` 
      The signal

    Returns
    -------
    :py:class:`numpy.ndarray` 
     the computed FFT features 
    
    """
    # sanity check
    assert signal.shape[1] == 5, "You should provide 5 pulses"
    if numpy.isnan(numpy.sum(signal)):
      return

    output_dim = int((self.nfft / 2) + 1)
    
    # get the frequencies
    f = numpy.fft.fftfreq(self.nfft) * self.framerate
   
    # we have 5 pulse signals, in different regions 
    ffts = numpy.zeros((5, output_dim))
    for i in range(5):
      ffts[i] = abs(numpy.fft.rfft(signal[:, i], n=self.nfft))

    fft = numpy.concatenate([ffts[0], ffts[1], ffts[2], ffts[3], ffts[4]])

    if self.debug: 
      from matplotlib import pyplot
      pyplot.plot(range(output_dim*5), fft, 'k')
      pyplot.title('Concatenation of spectra')
      pyplot.show()

    if numpy.isnan(numpy.sum(fft)):
      logger.warn("Feature not extracted")
      return
    if numpy.sum(fft) == 0:
      logger.warn("Feature not extracted")
      return

    return fft
