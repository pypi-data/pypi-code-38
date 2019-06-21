#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

from bob.ip.mtcnn import FaceDetector
from bob.bio.face.preprocessor import Base
import bob.ip.base
import bob.ip.color
import numpy

import logging
logger = logging.getLogger("bob.bio.htface")

class FaceDetectMTCNN(Base):
  """Performs a face detection using bob.ip.mtcnn

  **Parameters:**

  image_size
    Dimensions of the image after the crop
  """

  def __init__(
      self,
      image_size=(224, 224),
      margin=44,
      color_channel="rgb",
      **kwargs
  ):
    # call base class constructors
    self.color_channel = color_channel
    Base.__init__(self, **kwargs)
    self.image_size = image_size
    self.extractor = None
    self.margin = margin
    
    gamma = 0.2
    sigma0 = 1
    sigma1 = 2
    size = 5
    threshold = 10.
    alpha = 0.1 
    self.tan_triggs = bob.ip.base.TanTriggs(gamma, sigma0, sigma1, size, threshold, alpha)


  def __call__(self, image, annotations=None):
    """__call__(image, annotations = None) -> face

    Crops the face using the mtcnn face detector
    
    **Parameters:**

    image : 3D :py:class:`numpy.ndarray`
      The face image to be processed (3 channels only(.

    annotations : any
      Ignored.

    **Returns:**

    face : 3D :py:class:`numpy.ndarray`
      The cropped face.
    """
    
    #TODO: I need two preprocessors, one for the color and one for the gray
    color_channel = "rgb"
    #color_channel = "gray"

    # Loading the thing
    if self.extractor is None:
      self.extractor = FaceDetector()

    # In case the input is gray scale
    if len(image.shape)==2:
        image = bob.ip.color.gray_to_rgb(image.astype("uint8"))
      
    cropped_image = self.extractor.detect_crop(image, final_image_size=self.image_size, margin=self.margin)
    #cropped_image = self.extractor.detect_crop_align(image, final_image_size=self.image_size)
        
    if cropped_image is None:
        logger.warning("Face not found!! Retuning full image rescaled")

        #return None
        cropped_image = numpy.zeros(shape=( ([3] + list(self.image_size) )))
        bob.ip.base.scale(image, cropped_image)
      
    if color_channel == "gray":
        return self.tan_triggs(bob.ip.color.rgb_to_gray(cropped_image.astype("uint8")))
        #return bob.ip.color.rgb_to_gray(cropped_image.astype("uint8"))
    elif color_channel == "red":
        return cropped_image[0, :, :]
    elif color_channel == "green":
        return cropped_image[1, :, :]
    elif color_channel == "blue":
        return cropped_image[2, :, :]
    else:
        return cropped_image

