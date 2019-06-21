#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import bob.io.base
from bob.bio.base.preprocessor import Preprocessor as BasePreprocessor


class Preprocessor (BasePreprocessor):
  """
  Extracts the mask and pre-processes fingervein images.

  In this implementation, the finger image is (in this order):

    #. The image is pre-cropped to remove obvious non-finger image parts
    #. The mask is extrapolated from the image using one of our
       :py:class:`Masker`'s concrete implementations
    #. The image is normalized with one of our :py:class:`Normalizer`'s
    #. The image is filtered with one of our :py:class:`Filter`'s


  Parameters:

    crop (:py:class:`Cropper`): An object that will perform pre-cropping on
      the input image before a mask can be estimated. It removes parts of the
      image which are surely not part of the finger region you'll want to
      consider for the next steps.

    mask (:py:class:`Masker`): An object representing a Masker instance which
      will extrapolate the mask from the input image.

    normalize (:py:class:`Normalizer`): An object representing a Normalizer
      instance which will normalize the input image and its mask returning a
      new image mask pair.

    filter (:py:class:`Filter`): An object representing a Filter instance will
      will filter the input image and return a new filtered image. The filter
      instance also receives the extrapolated mask so it can, if desired, only
      apply the filtering operation where the mask has a value of ``True``

  """


  def __init__(self, crop, mask, normalize, filter, **kwargs):

    BasePreprocessor.__init__(self,
        crop = crop,
        mask = mask,
        normalize = normalize,
        filter = filter,
        **kwargs
        )

    self.crop = crop
    self.mask = mask
    self.normalize = normalize
    self.filter = filter


  def __call__(self, data, annotations=None):
    """Reads the input image or (image, mask) and prepares for fex.

    Parameters:

      data (numpy.ndarray): An 2D numpy array containing a gray-scaled image
        with dtype ``uint8``. The image maybe annotated with an RoI.


    Returns:

      numpy.ndarray: The image, preprocessed and normalized

      numpy.ndarray: A mask, of the same size of the image, indicating where
      the valid data for the object is.

    """

    data = self.crop(data)
    mask = self.mask(data)
    data, mask = self.normalize(data, mask)
    data = self.filter(data, mask)
    return data, mask


  def write_data(self, data, filename):
    '''Overrides the default method implementation to handle our tuple'''

    f = bob.io.base.HDF5File(filename, 'w')
    f.set('image', data[0])
    f.set('mask', data[1])


  def read_data(self, filename):
    '''Overrides the default method implementation to handle our tuple'''

    f = bob.io.base.HDF5File(filename, 'r')
    return f.read('image'), f.read('mask')
