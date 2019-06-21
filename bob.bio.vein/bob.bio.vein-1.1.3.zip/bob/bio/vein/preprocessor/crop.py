#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


'''Base utilities for pre-cropping images'''

import numpy


class Cropper(object):
    """This is the base class for all croppers

    It defines the minimum requirements for all derived cropper classes.


    """

    def __init__(self):
      pass


    def __call__(self, image):
      """Overwrite this method to implement your masking method


      Parameters:

        image (numpy.ndarray): A 2D numpy array of type ``uint8`` with the
          input image


      Returns:

        numpy.ndarray: A 2D numpy array of the same type as the input, with
        cropped rows and columns as per request

      """

      raise NotImplemented('You must implement the __call__ slot')


class FixedCrop(Cropper):
  """Implements cropping using a fixed suppression of border pixels

  The defaults supress no lines from the image and returns an image like the
  original. If an :py:class:`bob.bio.vein.database.AnnotatedArray` is passed,
  then we also check for its ``.metadata['roi']`` component and correct it so
  that annotated RoI points are consistent on the cropped image.


  .. note::

     Before choosing values, note you're responsible for knowing what is the
     orientation of images fed into this cropper.


  Parameters:

    top (:py:class:`int`, optional): Number of lines to suppress from the top
      of the image. The top of the image corresponds to ``y = 0``.

    bottom (:py:class:`int`, optional): Number of lines to suppress from the
      bottom of the image. The bottom of the image corresponds to ``y =
      height``.

    left (:py:class:`int`, optional): Number of lines to suppress from the left
      of the image. The left of the image corresponds to ``x = 0``.

    right (:py:class:`int`, optional): Number of lines to suppress from the
      right of the image. The right of the image corresponds to ``x = width``.

  """

  def __init__(self, top=0, bottom=0, left=0, right=0):
    self.top = top
    self.bottom = bottom
    self.left = left
    self.right = right


  def __call__(self, image):
    """Returns a big mask


    Parameters:

      image (numpy.ndarray): A 2D numpy array of type ``uint8`` with the
        input image


    Returns:

      numpy.ndarray: A 2D numpy array of type boolean with the caculated
      mask. ``True`` values correspond to regions where the finger is
      situated


    """

    # this should work even if limits are zeros
    h, w = image.shape
    retval = image[self.top:h-self.bottom, self.left:w-self.right]

    if hasattr(retval, 'metadata') and 'roi' in retval.metadata:
      # adjust roi points to new cropping
      retval = retval.copy() #don't override original
      h, w = retval.shape
      points = []
      for y, x in retval.metadata['roi']:
        y = max(y-self.top, 0) #adjust
        y = min(y, h-1) #verify it is not over the limits
        x = max(x-self.left, 0) #adjust
        x = min(x, w-1) #verify it is not over the limits
        points.append((y,x))
      retval.metadata['roi'] = points

    return retval


class NoCrop(FixedCrop):
  """Convenience: same as FixedCrop()"""

  def __init__(self):
    super(NoCrop, self).__init__(0, 0, 0, 0)
