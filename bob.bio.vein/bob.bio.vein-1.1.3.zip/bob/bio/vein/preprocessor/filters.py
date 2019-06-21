#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Base utilities for post-filtering vein images'''

import numpy


class Filter(object):
  '''Objects of this class filter the input image'''


  def __init__(self):
    pass


  def __call__(self, image, mask):
    '''Inputs image and mask and outputs a filtered version of the image


    Parameters:

      image (numpy.ndarray): raw image to filter as 2D array of unsigned
          8-bit integers

      mask (numpy.ndarray): mask to normalize as 2D array of booleans


    Returns:

      numpy.ndarray: A 2D boolean array with the same shape and data type of
      the input image representing the filtered image.

    '''

    raise NotImplemented('You must implement the __call__ slot')


class NoFilter(Filter):
  '''Applies no filtering on the input image, returning it without changes'''

  def __init__(self):
    pass


  def __call__(self, image, mask):
    '''Inputs image and mask and outputs the image, without changes


    Parameters:

      image (numpy.ndarray): raw image to filter as 2D array of unsigned
          8-bit integers

      mask (numpy.ndarray): mask to normalize as 2D array of booleans


    Returns:

      numpy.ndarray: A 2D boolean array with the same shape and data type of
      the input image representing the filtered image.

    '''

    return image


class HistogramEqualization(Filter):
  '''Applies histogram equalization on the input image inside the mask.

  In this implementation, only the pixels that lie inside the mask will be
  used to calculate the histogram equalization parameters. Because of this
  particularity, we don't use Bob's implementation for histogram equalization
  and have one based exclusively on scikit-image.
  '''


  def __init__(self):
    pass


  def __call__(self, image, mask):
    '''Applies histogram equalization on the input image, returns filtered


    Parameters:

      image (numpy.ndarray): raw image to filter as 2D array of unsigned
          8-bit integers

      mask (numpy.ndarray): mask to normalize as 2D array of booleans


    Returns:

      numpy.ndarray: A 2D boolean array with the same shape and data type of
      the input image representing the filtered image.

    '''

    from skimage.exposure import equalize_hist
    from skimage.exposure import rescale_intensity

    retval = rescale_intensity(equalize_hist(image, mask=mask), out_range = (0, 255))

    # make the parts outside the mask totally black
    retval[~mask] = 0

    return retval
