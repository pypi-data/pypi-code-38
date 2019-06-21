#!/usr/bin/env python
# encoding: utf-8

import numpy

from bob.core.log import setup
logger = setup("bob.pad.face")

from bob.bio.base.preprocessor import Preprocessor

import bob.ip.facedetect
import bob.ip.skincolorfilter

from bob.rppg.base.utils import crop_face
from bob.rppg.base.utils import build_bandpass_filter 

from bob.rppg.chrom.extract_utils import compute_mean_rgb
from bob.rppg.chrom.extract_utils import project_chrominance
from bob.rppg.chrom.extract_utils import compute_gray_diff
from bob.rppg.chrom.extract_utils import select_stable_frames 


class Chrom(Preprocessor, object):
  """Extract pulse signal from a video sequence.
  
  The pulse is extracted according to the CHROM algorithm.

  See the documentation of `bob.rppg.base`
  
  Attributes
  ----------
  skin_threshold : :obj:`float`
    The threshold for skin color probability
  skin_init : :obj:`bool`
    If you want to re-initailize the skin color distribution at each frame
  framerate : :obj:`int`
    The framerate of the video sequence.
  bp_order : :obj:`int`
    The order of the bandpass filter
  window_size : :obj:`int`
    The size of the window in the overlap-add procedure.
  motion : :obj:`float`
    The percentage of frames you want to select where the 
    signal is "stable". 0 mean all the sequence.
  debug : :obj:`bool`          
    Plot some stuff 
  skin_filter : :py:class:`bob.ip.skincolorfilter.SkinColorFilter` 
    The skin color filter 

  """
  
  def __init__(self, skin_threshold=0.5, skin_init=False, framerate=25, bp_order=32, window_size=0, motion=0.0, debug=False, **kwargs):
    """Init function

    Parameters
    ----------
    skin_threshold : :obj:`float`
      The threshold for skin color probability
    skin_init : :obj:`bool`
      If you want to re-initailize the skin color distribution at each frame
    framerate : :obj:`int`
      The framerate of the video sequence.
    bp_order : :obj:`int`
      The order of the bandpass filter
    window_size : :obj:`int`
      The size of the window in the overlap-add procedure.
    motion : :obj:`float`
      The percentage of frames you want to select where the 
      signal is "stable". 0 mean all the sequence.
    debug : :obj:`bool`          
      Plot some stuff 
    
    """
    super(Chrom, self).__init__()
    self.skin_threshold = skin_threshold
    self.skin_init = skin_init
    self.framerate = framerate
    self.bp_order = bp_order
    self.window_size = window_size
    self.motion = motion
    self.debug = debug
    self.skin_filter = bob.ip.skincolorfilter.SkinColorFilter()

  def __call__(self, frames, annotations=None):
    """Computes the pulse signal for the given frame sequence

    Parameters
    ----------
    frames : :py:class:`bob.bio.video.utils.FrameContainer`
      video data 
    annotations : :py:class:`dict`
      the face bounding box, as follows: ``{'topleft': (row, col), 'bottomright': (row, col)}``

    Returns
    -------
    :obj:`numpy.ndarray` 
      The pulse signal
    
    """
    video = frames.as_array()
    nb_frames = video.shape[0]
   
    # the pulse
    chrom = numpy.zeros((nb_frames, 2), dtype='float64')

    # build the bandpass filter 
    bandpass_filter = build_bandpass_filter(self.framerate, self.bp_order, plot=False)

    counter = 0
    previous_bbox = None
    for i, frame in enumerate(video):
      
      logger.debug("Processing frame {}/{}".format(counter, nb_frames))

      if self.debug:
        from matplotlib import pyplot
        pyplot.imshow(numpy.rollaxis(numpy.rollaxis(frame, 2),2))
        pyplot.show()
    
      # get the face
      try:
        topleft = annotations[str(i)]['topleft']
        bottomright = annotations[str(i)]['bottomright']
        size = (bottomright[0]-topleft[0], bottomright[1]-topleft[1])
        bbox = bob.ip.facedetect.BoundingBox(topleft, size)
        face = crop_face(frame, bbox, bbox.size[1])
      except (KeyError, ZeroDivisionError, TypeError) as e:
        logger.warning("No annotations ... running face detection")
        try:
          bbox, quality = bob.ip.facedetect.detect_single_face(frame)
          face = crop_face(frame, bbox, bbox.size[1])
        except:
          bbox = previous_bbox
          face = crop_face(frame, bbox, bbox.size[1])
          logger.warning("No detection, using bounding box from previous frame ...")

      # motion difference (if asked for)
      if self.motion > 0.0 and (i < (nb_frames - 1)) and (counter > 0):
        current = crop_face(frame, bbox, bbox.size[1])
        diff_motion[counter-1] = compute_gray_diff(face, current)
       
      if self.debug:
        from matplotlib import pyplot
        pyplot.imshow(numpy.rollaxis(numpy.rollaxis(face, 2),2))
        pyplot.show()

      # skin filter
      if counter == 0 or self.skin_init:
        self.skin_filter.estimate_gaussian_parameters(face)
        logger.debug("Skin color parameters:\nmean\n{0}\ncovariance\n{1}".format(self.skin_filter.mean, self.skin_filter.covariance))
      skin_mask = self.skin_filter.get_skin_mask(face, self.skin_threshold)

      if self.debug:
        from matplotlib import pyplot
        skin_mask_image = numpy.copy(face)
        skin_mask_image[:, skin_mask] = 255
        pyplot.imshow(numpy.rollaxis(numpy.rollaxis(skin_mask_image, 2),2))
        pyplot.show()

      # sometimes skin is not detected !
      if numpy.count_nonzero(skin_mask) != 0:

        # compute the mean rgb values of the skin pixels
        r,g,b = compute_mean_rgb(face, skin_mask)
        logger.debug("Mean color -> R = {0}, G = {1}, B = {2}".format(r,g,b))

        # project onto the chrominance colorspace
        chrom[counter] = project_chrominance(r, g, b)
        logger.debug("Chrominance -> X = {0}, Y = {1}".format(chrom[counter][0], chrom[counter][1]))

      else:
        logger.warn("No skin pixels detected in frame {0}, using previous value".format(i))
        # very unlikely, but it could happened and messed up all experiments (averaging of scores ...)
        if counter == 0:
          chrom[counter] = project_chrominance(128., 128., 128.)
        else:
          chrom[counter] = chrom[counter-1]


      # keep the result of the last detection in case you cannot find a face in the next frame
      previous_bbox = bbox
      counter +=1
    
    # select the most stable number of consecutive frames, if asked for
    if self.motion > 0.0:
      n_stable_frames_to_keep = int(self.motion * nb_frames)
      logger.info("Number of stable frames kept for motion -> {0}".format(n_stable_frames_to_keep))
      index = select_stable_frames(diff_motion, n_stable_frames_to_keep)
      logger.info("Stable segment -> {0} - {1}".format(index, index + n_stable_frames_to_keep))
      chrom = chrom[index:(index + n_stable_frames_to_keep),:]

    if self.debug:
      from matplotlib import pyplot
      f, axarr = pyplot.subplots(2, sharex=True)
      axarr[0].plot(range(chrom.shape[0]), chrom[:, 0], 'k')
      axarr[0].set_title("X value in the chrominance subspace")
      axarr[1].plot(range(chrom.shape[0]), chrom[:, 1], 'k')
      axarr[1].set_title("Y value in the chrominance subspace")
      pyplot.show()

    # now that we have the chrominance signals, apply bandpass
    from scipy.signal import filtfilt
    x_bandpassed = numpy.zeros(nb_frames, dtype='float64')
    y_bandpassed = numpy.zeros(nb_frames, dtype='float64')
    x_bandpassed = filtfilt(bandpass_filter, numpy.array([1]), chrom[:, 0])
    y_bandpassed = filtfilt(bandpass_filter, numpy.array([1]), chrom[:, 1])

    if self.debug:
      from matplotlib import pyplot
      f, axarr = pyplot.subplots(2, sharex=True)
      axarr[0].plot(range(x_bandpassed.shape[0]), x_bandpassed, 'k')
      axarr[0].set_title("X bandpassed")
      axarr[1].plot(range(y_bandpassed.shape[0]), y_bandpassed, 'k')
      axarr[1].set_title("Y bandpassed")
      pyplot.show()

    # build the final pulse signal
    alpha = numpy.std(x_bandpassed) / numpy.std(y_bandpassed)
    pulse = x_bandpassed - alpha * y_bandpassed

    # overlap-add if window_size != 0
    if self.window_size > 0:
      window_stride = self.window_size / 2
      for w in range(0, (len(pulse)-window_size), window_stride):
        pulse[w:w+window_size] = 0.0
        xw = x_bandpassed[w:w+window_size]
        yw = y_bandpassed[w:w+window_size]
        alpha = numpy.std(xw) / numpy.std(yw)
        sw = xw - alpha * yw
        sw *= numpy.hanning(window_size)
        pulse[w:w+window_size] += sw
    
    if self.debug:
      from matplotlib import pyplot
      f, axarr = pyplot.subplots(1)
      pyplot.plot(range(pulse.shape[0]), pulse, 'k')
      pyplot.title("Pulse signal")
      pyplot.show()

    return pulse
