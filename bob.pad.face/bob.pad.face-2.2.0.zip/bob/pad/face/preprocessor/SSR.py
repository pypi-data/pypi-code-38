#!/usr/bin/env python
# encoding: utf-8

import numpy

from bob.core.log import setup
logger = setup("bob.pad.face")

from bob.bio.base.preprocessor import Preprocessor

import bob.ip.facedetect
import bob.ip.skincolorfilter

from bob.rppg.base.utils import crop_face

from bob.rppg.ssr.ssr_utils import get_eigen
from bob.rppg.ssr.ssr_utils import plot_eigenvectors
from bob.rppg.ssr.ssr_utils import build_P


class SSR(Preprocessor, object):
  """Extract pulse signal from a video sequence.
  
  The pulse is extracted according to the SSR algorithm.

  See the documentation of :py:module::`bob.rppg.base`

  Attributes
  ----------
  skin_threshold: float
    The threshold for skin color probability
  skin_init: bool
    If you want to re-initailize the skin color distribution at each frame
  stride: int
    The temporal stride. 
  debug: boolean          
    Plot some stuff 
  skin_filter: :py:class::`bob.ip.skincolorfilter.SkinColorFilter` 
    The skin color filter 

  """
  
  def __init__(self, skin_threshold=0.5, skin_init=False, stride=25, debug=False, **kwargs):
    """Init function

    Parameters
    ----------
    skin_threshold: float
      The threshold for skin color probability
    skin_init: bool
      If you want to re-initailize the skin color distribution at each frame
    stride: int
      The temporal stride. 
    debug: boolean          
      Plot some stuff 

    """
    super(SSR, self).__init__()
    self.skin_threshold = skin_threshold
    self.skin_init = skin_init
    self.stride = stride
    self.debug = debug
    self.skin_filter = bob.ip.skincolorfilter.SkinColorFilter()


  def __call__(self, frames, annotations):
    """Computes the pulse signal for the given frame sequence

    Parameters
    ----------
    frames: :py:class:`bob.bio.video.utils.FrameContainer`
      video data 
    annotations: :py:class:`dict`
      the face bounding box, as follows: ``{'topleft': (row, col), 'bottomright': (row, col)}``

    Returns
    -------
    pulse: numpy.ndarray 
      The pulse signal
    
    """
    video = frames.as_array()
    nb_frames = video.shape[0]

    # the result -> the pulse signal 
    output_data = numpy.zeros(nb_frames, dtype='float64')

    # store the eigenvalues and the eigenvectors at each frame 
    eigenvalues = numpy.zeros((3, nb_frames), dtype='float64')
    eigenvectors = numpy.zeros((3, 3, nb_frames), dtype='float64')

    counter = 0
    previous_bbox = None
    previous_skin_pixels = None

    for i, frame in enumerate(video):

      logger.debug("Processing frame %d/%d...", i, nb_frames)

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

      if self.debug:
        from matplotlib import pyplot
        pyplot.imshow(numpy.rollaxis(numpy.rollaxis(face, 2),2))
        pyplot.show()

      # skin filter
      if counter == 0 or self.skin_init:
        self.skin_filter.estimate_gaussian_parameters(face)
        logger.debug("Skin color parameters:\nmean\n{0}\ncovariance\n{1}".format(self.skin_filter.mean, self.skin_filter.covariance))
      
      skin_mask = self.skin_filter.get_skin_mask(face, self.skin_threshold)
      skin_pixels = face[:, skin_mask]
      skin_pixels = skin_pixels.astype('float64') / 255.0

      if self.debug:
        from matplotlib import pyplot
        skin_mask_image = numpy.copy(face)
        skin_mask_image[:, skin_mask] = 255
        pyplot.title("skin pixels in frame {0}".format(i))
        pyplot.imshow(numpy.rollaxis(numpy.rollaxis(skin_mask_image, 2),2))
        pyplot.show()
      
      # no skin pixels have ben detected ... using the previous ones
      if skin_pixels.shape[1] == 0:
        skin_pixels = previous_skin_pixels 
        logger.warn("No skin pixels detected, using the previous ones")

      # build c matrix and get eigenvectors and eigenvalues
      eigenvalues[:, counter], eigenvectors[:, :, counter] = get_eigen(skin_pixels)
      
      if self.debug:
        plot_eigenvectors(skin_pixels, eigenvectors[:, :, counter])

      # build P and add it to the pulse signal
      if counter >= self.stride:
        tau = counter - self.stride
        p = build_P(counter, self.stride, eigenvectors, eigenvalues)
        output_data[tau:counter] += (p - numpy.mean(p)) 
        
      previous_bbox = bbox
      previous_skin_pixels = skin_pixels
      counter += 1

    if self.debug:
      import matplotlib.pyplot as plt
      fig = plt.figure()
      ax = fig.add_subplot(111)
      ax.plot(range(nb_frames), output_data)
      plt.show()

    return output_data
