#!/usr/bin/env python
# encoding: utf-8

import numpy

from bob.core.log import setup
logger = setup("bob.pad.face")

from bob.bio.base.preprocessor import Preprocessor

from bob.rppg.base.utils import build_bandpass_filter 
import bob.ip.dlib

from bob.rppg.cvpr14.extract_utils import kp66_to_mask
from bob.rppg.cvpr14.extract_utils import compute_average_colors_mask
from bob.rppg.cvpr14.filter_utils import detrend
from bob.rppg.cvpr14.filter_utils import average


class LiPulseExtraction(Preprocessor):
  """Extract pulse signal from a video sequence.
  
  The pulse is extracted according to a simplified version of Li's CVPR 14 algorithm.

  It is described in:
  X. Li, J, Komulainen, G. Zhao, P-C Yuen and M. Pietikäinen
  "Generalized face anti-spoofing by detecting pulse from face videos"
  Intl Conf on Pattern Recognition (ICPR), 2016

  See the documentation of `bob.rppg.base`

  Note that this is a simplified version of the original 
  pulse extraction algorithms (mask detection in each 
  frame instead of tracking, no illumination correction,
  no motion pruning)

  Attributes
  ----------
  indent : :obj:`int`
    Indent (in percent of the face width) to apply to keypoints to get the mask.
  lamda_ : :obj:`int`
    the lamba value of the detrend filter
  window : :obj:`int`
    The size of the window of the average filter 
  framerate : :obj:`int`
    The framerate of the video sequence.
  bp_order : :obj:`int`
    The order of the bandpass filter
  debug : :obj:`bool`
    Plot some stuff 
  
  """
  
  def __init__(self, indent = 10, lambda_ = 300, window = 3, framerate = 25, bp_order = 32, debug=False, **kwargs):
    """Init function

    Parameters
    ----------
    indent : :obj:`int`
      Indent (in percent of the face width) to apply to keypoints to get the mask.
    lamda_ : :obj:`int`
      the lamba value of the detrend filter
    window : :obj:`int`
      The size of the window of the average filter 
    framerate : :obj:`int`
      The framerate of the video sequence.
    bp_order : :obj:`int`
      The order of the bandpass filter
    debug : :obj:`bool`
      Plot some stuff 

    """
    super(LiPulseExtraction, self).__init__(**kwargs)
    self.indent = indent
    self.lambda_ = lambda_
    self.window = window
    self.framerate = framerate
    self.bp_order = bp_order
    self.debug = debug

  def __call__(self, frames, annotations=None):
    """Computes the pulse signal for the given frame sequence

    Parameters
    ----------
    frames: :py:class:`bob.bio.video.utils.FrameContainer`
      video data 
    annotations: :py:class:`dict`
      the face bounding box, as follows: ``{'topleft': (row, col), 'bottomright': (row, col)}``

    Returns
    -------
    :obj:`numpy.ndarray` 
      The pulse signal, in each color channel (RGB)  
    
    """
    video = frames.as_array()
    nb_frames = video.shape[0]

    # the mean color of the face along the sequence
    face_color = numpy.zeros((nb_frames, 3), dtype='float64')

    # build the bandpass filter
    bandpass_filter = build_bandpass_filter(self.framerate, self.bp_order, plot=False)

    # landmarks detection
    detector = bob.ip.dlib.DlibLandmarkExtraction()

    counter = 0
    previous_ldms = None
    for i, frame in enumerate(video):

      logger.debug("Processing frame {}/{}".format(counter, nb_frames))
      if self.debug:
        from matplotlib import pyplot
        pyplot.imshow(numpy.rollaxis(numpy.rollaxis(frame, 2),2))
        pyplot.show()
     
      # detect landmarks
      ldms = detector(frame)
      
      if ldms is None:
        logger.warning("Landmarks not detected ...")

        # looks like some videos from replay mobile are upside down !
        rotated_shape = bob.ip.base.rotated_output_shape(frame, 180)
        frame_rotated = numpy.ndarray(rotated_shape, dtype=numpy.float64)
        from bob.ip.base import rotate
        bob.ip.base.rotate(frame, frame_rotated, 180)
        frame_rotated = frame_rotated.astype(numpy.uint8)
        logger.warning("Rotating 180 degrees ...")

        # check the rotated frame
        if self.debug:
          from matplotlib import pyplot
          pyplot.imshow(numpy.rollaxis(numpy.rollaxis(frame_rotated, 2),2))
          pyplot.show()
        
        ldms = detector(frame_rotated)
        # if landmarks are still not detected, do nothing
        if ldms is None:
          ldms = previous_ldms
          # so do nothing ...
          logger.warning("No mask detected in frame {}".format(i))
          face_color[i] = [0, 0, 0]
          continue
        
        frame = frame_rotated
        
      # if landmarks are still not detected, use the one from previous frame (if any)
      if ldms is None:
        if previous_ldms is None:
          logger.warning("No mask detected in frame {}".format(i))
          face_color[i] = [0, 0, 0]
          continue
        else: 
          ldms = previous_ldms
          logger.warning("Frame {}: no landmarks detected, using the ones from previous frame".format(i))

      if self.debug:
        from matplotlib import pyplot
        display = numpy.copy(frame)
        for p in ldms:
          bob.ip.draw.plus(display, p, radius=5, color=(255, 0, 0))
        pyplot.imshow(numpy.rollaxis(numpy.rollaxis(display, 2),2))
        pyplot.show()

      ldms = numpy.array(ldms)
      mask_points, mask = kp66_to_mask(frame, ldms, self.indent, self.debug)
      face_color[i] = compute_average_colors_mask(frame, mask, self.debug)

      previous_ldms = ldms 
      counter += 1

    pulse = numpy.zeros((nb_frames, 3), dtype='float64')
    for i in range(3):
      # detrend
      detrended = detrend(face_color[:, i], self.lambda_)
      # average
      averaged = average(detrended, self.window)
      # bandpass
      from scipy.signal import filtfilt
      pulse[:, i] = filtfilt(bandpass_filter, numpy.array([1]), averaged)

    if self.debug: 
      colors = ['r', 'g', 'b']
      from matplotlib import pyplot
      for i in range(3):
        f, ax = pyplot.subplots(2, sharex=True)
        ax[0].plot(range(face_color.shape[0]), face_color[:, i], colors[i])
        ax[0].set_title('Original color signal')
        ax[1].plot(range(face_color.shape[0]), pulse[:, i], colors[i])
        ax[1].set_title('Pulse signal')
        pyplot.show()

    return pulse 
