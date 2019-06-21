#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Base utilities for normalization'''

import math
import numpy
from PIL import Image


class Normalizer(object):
  '''Objects of this class normalize the input image orientation and scale'''


  def __init__(self):
    pass


  def __call__(self, image, mask):
    '''Inputs image and mask and outputs a normalized version of those


    Parameters:

      image (numpy.ndarray): raw image to normalize as 2D array of unsigned
          8-bit integers

      mask (numpy.ndarray): mask to normalize as 2D array of booleans


    Returns:

      numpy.ndarray: A 2D boolean array with the same shape and data type of
      the input image representing the newly aligned image.

      numpy.ndarray: A 2D boolean array with the same shape and data type of
      the input mask representing the newly aligned mask.

    '''

    raise NotImplemented('You must implement the __call__ slot')



class NoNormalization(Normalizer):
  '''Trivial implementation with no normalization'''


  def __init__(self):
    pass


  def __call__(self, image, mask):
    '''Returns the input parameters, without changing them


    Parameters:

      image (numpy.ndarray): raw image to normalize as 2D array of unsigned
          8-bit integers

      mask (numpy.ndarray): mask to normalize as 2D array of booleans


    Returns:

      numpy.ndarray: A 2D boolean array with the same shape and data type of
      the input image representing the newly aligned image.

      numpy.ndarray: A 2D boolean array with the same shape and data type of
      the input mask representing the newly aligned mask.

    '''

    return image, mask



class HuangNormalization(Normalizer):
  '''Simple finger normalization from Huang et. al

  Based on B. Huang, Y. Dai, R. Li, D. Tang and W. Li, Finger-vein
  authentication based on wide line detector and pattern normalization,
  Proceedings on 20th International Conference on Pattern Recognition (ICPR),
  2010.

  This implementation aligns the finger to the centre of the image using an
  affine transformation. Elliptic projection which is described in the
  referenced paper is **not** included.

  In order to defined the affine transformation to be performed, the
  algorithm first calculates the center for each edge (column wise) and
  calculates the best linear fit parameters for a straight line passing
  through those points.
  '''

  def __init__(self, padding_width=5, padding_constant=51):
    self.padding_width = padding_width
    self.padding_constant = padding_constant


  def __call__(self, image, mask):
    '''Inputs image and mask and outputs a normalized version of those


    Parameters:

      image (numpy.ndarray): raw image to normalize as 2D array of unsigned
          8-bit integers

      mask (numpy.ndarray): mask to normalize as 2D array of booleans


    Returns:

      numpy.ndarray: A 2D boolean array with the same shape and data type of
      the input image representing the newly aligned image.

      numpy.ndarray: A 2D boolean array with the same shape and data type of
      the input mask representing the newly aligned mask.

    '''

    img_h, img_w = image.shape

    # Calculates the mask edges along the columns
    edges = numpy.zeros((2, mask.shape[1]), dtype=int)

    edges[0,:] = mask.argmax(axis=0) # get upper edges
    edges[1,:] = len(mask) - numpy.flipud(mask).argmax(axis=0) - 1

    bl = edges.mean(axis=0) #baseline
    x = numpy.arange(0, edges.shape[1])
    A = numpy.vstack([x, numpy.ones(len(x))]).T

    # Fit a straight line through the base line points
    w = numpy.linalg.lstsq(A,bl)[0] # obtaining the parameters

    angle = -1*math.atan(w[0])  # Rotation
    tr = img_h/2 - w[1]         # Translation
    scale = 1.0                 # Scale

    #Affine transformation parameters
    sx=sy=scale
    cosine = math.cos(angle)
    sine = math.sin(angle)

    a = cosine/sx
    b = -sine/sy
    #b = sine/sx
    c = 0 #Translation in x

    d = sine/sx
    e = cosine/sy
    f = tr #Translation in y
    #d = -sine/sy
    #e = cosine/sy
    #f = 0

    g = 0
    h = 0
    #h=tr
    i = 1

    T = numpy.matrix([[a,b,c],[d,e,f],[g,h,i]])
    Tinv = numpy.linalg.inv(T)
    Tinvtuple = (Tinv[0,0],Tinv[0,1], Tinv[0,2], Tinv[1,0],Tinv[1,1],Tinv[1,2])

    def _afftrans(img):
      '''Applies the affine transform on the resulting image'''

      t = Image.fromarray(img.astype('uint8'))
      w, h = t.size #pillow image is encoded w, h
      w += 2*self.padding_width
      h += 2*self.padding_width
      t = t.transform(
          (w,h),
          Image.AFFINE,
          Tinvtuple,
          resample=Image.BICUBIC,
          fill=self.padding_constant)

      return numpy.array(t).astype(img.dtype)

    return _afftrans(image), _afftrans(mask)
