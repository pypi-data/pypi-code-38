#!/usr/bin/env python
# encoding: utf-8

import numpy

from bob.core.log import setup
logger = setup("bob.pad.face")

from bob.bio.base.preprocessor import Preprocessor

from bob.rppg.base.utils import build_bandpass_filter 
import bob.ip.dlib

from bob.rppg.cvpr14.extract_utils import get_mask
from bob.rppg.cvpr14.extract_utils import compute_average_colors_mask


class PPGSecure(Preprocessor):
  """
  This class extract the pulse signal from a video sequence.
  
  The pulse is extracted according to what is described in 
  the following article:

  E.M Nowara, A. Sabharwal and A. Veeraraghavan,
  "PPGSecure: Biometric Presentation Attack Detection using Photoplethysmograms",
  IEEE Intl Conf. on Automatic Face and Gesture Recognition, 2017.

  Attributes
  ----------
  framerate : :obj:`int`
    The framerate of the video sequence.
  bp_order : :obj:`int` 
    The order of the bandpass filter
  debug : :obj:`bool` 
    Plot some stuff 
  
  """
  def __init__(self, framerate=25, bp_order=32, debug=False, **kwargs):
    """Init function

    Parameters
    ----------
    framerate : :obj:`int`
      The framerate of the video sequence.
    bp_order : :obj:`int` 
      The order of the bandpass filter
    debug : :obj:`bool` 
      Plot some stuff 
    
    """
    super(PPGSecure, self).__init__(**kwargs)
    self.framerate = framerate
    self.bp_order = bp_order
    self.debug = debug
    
    # build the bandpass filter
    self.bandpass_filter = build_bandpass_filter(self.framerate, self.bp_order, min_freq=0.5, max_freq=5, plot=False)
    
    # landmarks detector
    self.detector = bob.ip.dlib.DlibLandmarkExtraction()

  def __call__(self, frames, annotations):
    """Compute the pulse signal for the given frame sequence

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

    # the mean of the green color of the different ROIs along the sequence
    green_mean = numpy.zeros((nb_frames, 5), dtype='float64')

    previous_ldms = None
    for i, frame in enumerate(video):

      logger.debug("Processing frame {}/{}".format(i, nb_frames))
      if self.debug:
        from matplotlib import pyplot
        pyplot.imshow(numpy.rollaxis(numpy.rollaxis(frame, 2),2))
        pyplot.show()
     
      # detect landmarks
      ldms = self.detector(frame)
      
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
        
        ldms = self.detector(frame_rotated)
        # if landmarks are still not detected, do nothing
        if ldms is None:
          ldms = previous_ldms
          # so do nothing ...
          logger.warning("No mask detected in frame {}".format(i))
          green_mean[i] = [0, 0, 0, 0, 0]
          continue
        
        frame = frame_rotated
        
      # if landmarks are still not detected, use the one from previous frame (if any)
      if ldms is None:
        if previous_ldms is None:
          logger.warning("No mask detected in frame {}".format(i))
          green_mean[i] = [0, 0, 0, 0, 0]
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

      # get the mask and the green value in the different ROIs
      masks = self._get_masks(frame, ldms)
      for k in range(5):
        green_mean[i, k] = compute_average_colors_mask(frame, masks[k], self.debug)[1]

      previous_ldms = ldms 

    pulses = numpy.zeros((nb_frames, 5), dtype='float64')
    for k in range(5):
      # substract mean
      green_mean[:, k] = green_mean[:, k] - numpy.mean(green_mean[:, k])
      # bandpass
      from scipy.signal import filtfilt
      pulses[:, k] = filtfilt(self.bandpass_filter, numpy.array([1]), green_mean[:, k])

    if self.debug: 
      from matplotlib import pyplot
      for k in range(5):
        f, ax = pyplot.subplots(2, sharex=True)
        ax[0].plot(range(green_mean.shape[0]), green_mean[:, k], 'g')
        ax[0].set_title('Original color signal')
        ax[1].plot(range(green_mean.shape[0]), pulses[:, k], 'g')
        ax[1].set_title('Pulse signal')
        pyplot.show()

    return pulses 


  def _get_masks(self, image, ldms):
    """Get the 5 masks for rPPG signal extraction

    Parameters
    ----------
    ldms: numpy.ndarray
      The landmarks, as retrieved by bob.ip.dlib.DlibLandmarkExtraction()

    Returns
    -------
    masks: :py:obj:`list` of numpy.ndarray
      A list containing the different mask as a boolean array
        
    """
    masks = []

    # mask 1: forehead
    # defined by 12 points: upper eyebrows (points 18 to 27)
    # plus two additional points:
    # - above 18, at a distance of (18-27)/2
    # - above 27, at a distance of (18-27)/2
    #
    # Note 0 -> y, 1 -> x
    mask_points = []
    for k in range(17, 27):
      mask_points.append([int(ldms[k, 0]), int(ldms[k, 1])])
    above_20_x = int(ldms[19, 1])
    above_20_y = int(ldms[19, 0]) - int(abs(ldms[17, 1] - ldms[26, 1]) / 3)
    above_25_x = int(ldms[24, 1])
    above_25_y = int(ldms[24, 0]) - int(abs(ldms[17, 1] - ldms[26, 1]) / 3)
    mask_points.append([above_25_y, above_25_x])
    mask_points.append([above_20_y, above_20_x])
    masks.append(get_mask(image, mask_points))
    
    # mask 2: right cheek (left-hand side when looking at the screen)
    # defined by points 1-7 + 49 + 32 + 42
    mask_points = []
    for k in range(7):
      mask_points.append([int(ldms[k, 0]), int(ldms[k, 1])])
    mask_points.append([int(ldms[48, 0]), int(ldms[48, 1])])
    mask_points.append([int(ldms[31, 0]), int(ldms[31, 1])])
    mask_points.append([int(ldms[41, 0]), int(ldms[41, 1])])
    masks.append(get_mask(image, mask_points))

    # mask 3: left cheek 
    # defined by points 17-11 + 55 + 36 + 47
    mask_points = []
    for k in range(16, 10, -1):
      mask_points.append([int(ldms[k, 0]), int(ldms[k, 1])])
    mask_points.append([int(ldms[54, 0]), int(ldms[54, 1])])
    mask_points.append([int(ldms[35, 0]), int(ldms[35, 1])])
    mask_points.append([int(ldms[46, 0]), int(ldms[46, 1])])
    masks.append(get_mask(image, mask_points))
   
    # mask 4: right above shoulder
    mask_points = []
    mask_points.append([int(ldms[2, 0]), int(ldms[2, 1] - 10)])
    mask_points.append([int(ldms[2, 0]), int(ldms[2, 1] - 60)])
    mask_points.append([int(ldms[2, 0] + 50), int(ldms[2, 1] - 60)])
    mask_points.append([int(ldms[2, 0] + 50), int(ldms[2, 1] - 10)])
    masks.append(get_mask(image, mask_points))

    # mask 5: left above shoulder
    mask_points = []
    mask_points.append([int(ldms[14, 0]), int(ldms[14, 1] + 10)])
    mask_points.append([int(ldms[14, 0]), int(ldms[14, 1] + 60)])
    mask_points.append([int(ldms[14, 0] + 50), int(ldms[14, 1] + 60)])
    mask_points.append([int(ldms[14, 0] + 50), int(ldms[14, 1] + 10)])
    masks.append(get_mask(image, mask_points))

    return masks
