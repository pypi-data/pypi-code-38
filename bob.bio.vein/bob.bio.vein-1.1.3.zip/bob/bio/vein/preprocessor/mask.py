#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Base utilities for mask processing'''

import math
import numpy
import scipy.ndimage
import skimage.filters
import skimage.morphology

from .utils import poly_to_mask


class Padder(object):
  """A class that pads the input image returning a new object


  Parameters:

    padding_width (:py:obj:`int`, optional): How much padding (in pixels) to
      add around the borders of the input image. We normally always keep this
      value on its default (5 pixels). This parameter is always used before
      normalizing the finger orientation.

    padding_constant (:py:obj:`int`, optional): What is the value of the pixels
      added to the padding. This number should be a value between 0 and 255.
      (From Pedro Tome: for UTFVP (high-quality samples), use 0. For the VERA
      Fingervein database (low-quality samples), use 51 (that corresponds to
      0.2 in a float image with values between 0 and 1). This parameter is
      always used before normalizing the finger orientation.

  """

  def __init__(self, padding_width = 5, padding_constant = 51):

    self.padding_width = padding_width
    self.padding_constant = padding_constant


  def __call__(self, image):
    '''Inputs an image, returns a padded (larger) image

      Parameters:

        image (numpy.ndarray): A 2D numpy array of type ``uint8`` with the
          input image


      Returns:

        numpy.ndarray: A 2D numpy array of the same type as the input, but with
        the extra padding

    '''

    return numpy.pad(image, self.padding_width, 'constant',
        constant_values = self.padding_constant)



class Masker(object):
    """This is the base class for all maskers

    It defines the minimum requirements for all derived masker classes.


    """

    def __init__(self):
      pass


    def __call__(self, image):
      """Overwrite this method to implement your masking method


      Parameters:

        image (numpy.ndarray): A 2D numpy array of type ``uint8`` with the
          input image


      Returns:

        numpy.ndarray: A 2D numpy array of type boolean with the caculated
        mask. ``True`` values correspond to regions where the finger is
        situated

      """

      raise NotImplemented('You must implement the __call__ slot')


class FixedMask(Masker):
  """Implements masking using a fixed suppression of border pixels

  The defaults mask no lines from the image and returns a mask of the same size
  of the original image where all values are ``True``.


  .. note::

     Before choosing values, note you're responsible for knowing what is the
     orientation of images fed into this masker.


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

    retval = numpy.zeros(image.shape, dtype='bool')
    h, w = image.shape
    retval[self.top:h-self.bottom, self.left:w-self.right] = True
    return retval


class NoMask(FixedMask):
  """Convenience: same as FixedMask()"""

  def __init__(self):
    super(NoMask, self).__init__(0, 0, 0, 0)


class AnnotatedRoIMask(Masker):
  """Devises the mask from the annotated RoI"""


  def __init__(self):
    pass


  def __call__(self, image):
    """Returns a mask extrapolated from RoI annotations


    Parameters:

      image (bob.bio.vein.database.AnnotatedArray): A 2D numpy array of type
        ``uint8`` with the input image containing an attribute called
        ``metadata`` (a python dictionary). The ``metadata`` object just
        contain a key called ``roi`` containing the annotated points


    Returns:

      numpy.ndarray: A 2D numpy array of type boolean with the caculated
      mask. ``True`` values correspond to regions where the finger is
      situated


    """

    return poly_to_mask(image.shape, image.metadata['roi'])


class KonoMask(Masker):
  """Estimates the finger region given an input NIR image using Kono et al.

  This method is based on the work of M. Kono, H. Ueki and S.  Umemura.
  Near-infrared finger vein patterns for personal identification, Applied
  Optics, Vol. 41, Issue 35, pp. 7429-7436 (2002).


  Parameters:

    sigma (:py:obj:`float`, optional): The standard deviation of the gaussian
      blur filter to apply for low-passing the input image (background
      extraction). Defaults to ``5``.

    padder (:py:class:`Padder`, optional): If passed, will pad the image before
      evaluating the mask. The returned value will have the padding removed and
      is, therefore, of the exact size of the input image.

  """

  def __init__(self, sigma=5, padder=Padder()):

    self.sigma = sigma
    self.padder = padder


  def __call__(self, image):
    '''Inputs an image, returns a mask (numpy boolean array)

      Parameters:

        image (numpy.ndarray): A 2D numpy array of type ``uint8`` with the
          input image


      Returns:

        numpy.ndarray: A 2D numpy array of type boolean with the caculated
        mask. ``True`` values correspond to regions where the finger is
        situated

    '''

    image = image if self.padder is None else self.padder(image)
    if image.dtype == numpy.uint8: image = image.astype('float64')/255.

    img_h,img_w = image.shape

    # Determine lower half starting point
    if numpy.mod(img_h,2) == 0:
        half_img_h = img_h/2 + 1
    else:
        half_img_h = numpy.ceil(img_h/2)

    #Construct filter kernel
    winsize = numpy.ceil(4*self.sigma)

    x = numpy.arange(-winsize, winsize+1)
    y = numpy.arange(-winsize, winsize+1)
    X, Y = numpy.meshgrid(x, y)

    hy = (-Y/(2*math.pi*self.sigma**4)) * \
        numpy.exp(-(X**2 + Y**2)/(2*self.sigma**2))

    # Filter the image with the directional kernel
    fy = scipy.ndimage.convolve(image, hy, mode='nearest')

    # Upper part of filtred image
    img_filt_up = fy[0:half_img_h,:]
    y_up = img_filt_up.argmax(axis=0)

    # Lower part of filtred image
    img_filt_lo = fy[half_img_h-1:,:]
    y_lo = img_filt_lo.argmin(axis=0)

    # Fill region between upper and lower edges
    finger_mask = numpy.ndarray(image.shape, numpy.bool)
    finger_mask[:,:] = False

    for i in range(0,img_w):
      finger_mask[y_up[i]:y_lo[i]+image.shape[0]-half_img_h+2,i] = True

    if not self.padder:
      return finger_mask
    else:
      w = self.padder.padding_width
      return finger_mask[w:-w,w:-w]


class LeeMask(Masker):
  """Estimates the finger region given an input NIR image using Lee et al.

  This method is based on the work of Finger vein recognition using
  minutia-based alignment and local binary pattern-based feature extraction,
  E.C. Lee, H.C. Lee and K.R. Park, International Journal of Imaging Systems
  and Technology, Volume 19, Issue 3, September 2009, Pages 175--178, doi:
  10.1002/ima.20193

  This code is based on the Matlab implementation by Bram Ton, available at:

  https://nl.mathworks.com/matlabcentral/fileexchange/35752-finger-region-localisation/content/lee_region.m

  In this method, we calculate the mask of the finger independently for each
  column of the input image. Firstly, the image is convolved with a [1,-1]
  filter of size ``(self.filter_height, self.filter_width)``. Then, the upper and
  lower parts of the resulting filtered image are separated. The location of
  the maxima in the upper part is located. The same goes for the location of
  the minima in the lower part. The mask is then calculated, per column, by
  considering it starts in the point where the maxima is in the upper part and
  goes up to the point where the minima is detected on the lower part.


  Parameters:

    filter_height (:py:obj:`int`, optional): Height of contour mask in pixels,
      must be an even number

    filter_width (:py:obj:`int`, optional): Width of the contour mask in pixels

  """

  def __init__(self, filter_height = 4, filter_width = 40, padder=Padder()):
    self.filter_height = filter_height
    self.filter_width = filter_width
    self.padder = padder


  def __call__(self, image):
    '''Inputs an image, returns a mask (numpy boolean array)

      Parameters:

        image (numpy.ndarray): A 2D numpy array of type ``uint8`` with the
          input image


      Returns:

        numpy.ndarray: A 2D numpy array of type boolean with the caculated
        mask. ``True`` values correspond to regions where the finger is
        situated

    '''

    image = image if self.padder is None else self.padder(image)
    if image.dtype == numpy.uint8: image = image.astype('float64')/255.

    img_h,img_w = image.shape

    # Determine lower half starting point
    half_img_h = int(img_h/2)

    # Construct mask for filtering
    mask = numpy.ones((self.filter_height,self.filter_width), dtype='float64')
    mask[int(self.filter_height/2.):,:] = -1.0

    img_filt = scipy.ndimage.convolve(image, mask, mode='nearest')

    # Upper part of filtered image
    img_filt_up = img_filt[:half_img_h,:]
    y_up = img_filt_up.argmax(axis=0)

    # Lower part of filtered image
    img_filt_lo = img_filt[half_img_h:,:]
    y_lo = img_filt_lo.argmin(axis=0)

    # Translation: for all columns of the input image, set to True all pixels
    # of the mask from index where the maxima occurred in the upper part until
    # the index where the minima occurred in the lower part.
    finger_mask = numpy.zeros(image.shape, dtype='bool')
    for i in range(img_filt.shape[1]):
      finger_mask[y_up[i]:(y_lo[i]+img_filt_lo.shape[0]+1), i] = True

    if not self.padder:
      return finger_mask
    else:
      w = self.padder.padding_width
      return finger_mask[w:-w,w:-w]


class TomesLeeMask(Masker):
  """Estimates the finger region given an input NIR image using Lee et al.

  This method is based on the work of Finger vein recognition using
  minutia-based alignment and local binary pattern-based feature extraction,
  E.C. Lee, H.C. Lee and K.R. Park, International Journal of Imaging Systems
  and Technology, Volume 19, Issue 3, September 2009, Pages 175--178, doi:
  10.1002/ima.20193

  This code is a variant of the Matlab implementation by Bram Ton, available
  at:

  https://nl.mathworks.com/matlabcentral/fileexchange/35752-finger-region-localisation/content/lee_region.m

  In this variant from Pedro Tome, the technique of filtering the image with
  a horizontal filter is also applied on the vertical axis. The objective is to
  find better limits on the horizontal axis in case finger images show the
  finger tip. If that is not your case, you may use the original variant
  :py:class:`LeeMask` above.


  Parameters:

    filter_height (:py:obj:`int`, optional): Height of contour mask in pixels,
      must be an even number

    filter_width (:py:obj:`int`, optional): Width of the contour mask in pixels

  """

  def __init__(self, filter_height = 4, filter_width = 40, padder=Padder()):
    self.filter_height = filter_height
    self.filter_width = filter_width
    self.padder = padder


  def __call__(self, image):
    '''Inputs an image, returns a mask (numpy boolean array)

      Parameters:

        image (numpy.ndarray): A 2D numpy array of type ``uint8`` with the
          input image


      Returns:

        numpy.ndarray: A 2D numpy array of type boolean with the caculated
        mask. ``True`` values correspond to regions where the finger is
        situated

    '''

    image = image if self.padder is None else self.padder(image)
    if image.dtype == numpy.uint8: image = image.astype('float64')/255.

    img_h,img_w = image.shape

    # Determine lower half starting point
    half_img_h = img_h/2
    half_img_w = img_w/2

    # Construct mask for filtering (up-bottom direction)
    mask = numpy.ones((self.filter_height, self.filter_width), dtype='float64')
    mask[int(self.filter_height/2.):,:] = -1.0

    img_filt = scipy.ndimage.convolve(image, mask, mode='nearest')

    # Upper part of filtred image
    img_filt_up = img_filt[:int(half_img_h),:]
    y_up = img_filt_up.argmax(axis=0)

    # Lower part of filtred image
    img_filt_lo = img_filt[int(half_img_h):,:]
    y_lo = img_filt_lo.argmin(axis=0)

    img_filt = scipy.ndimage.convolve(image, mask.T, mode='nearest')

    # Left part of filtered image
    img_filt_lf = img_filt[:,:int(half_img_w)]
    y_lf = img_filt_lf.argmax(axis=1)

    # Right part of filtred image
    img_filt_rg = img_filt[:,int(half_img_w):]
    y_rg = img_filt_rg.argmin(axis=1)

    finger_mask = numpy.zeros(image.shape, dtype='bool')

    for i in range(0,y_up.size):
      finger_mask[y_up[i]:y_lo[i]+img_filt_lo.shape[0]+1,i] = True

    # Left region
    for i in range(0,y_lf.size):
      finger_mask[i,0:y_lf[i]+1] = False

    # Right region has always the finger ending, crop the padding with the
    # meadian
    finger_mask[:,int(numpy.median(y_rg)+img_filt_rg.shape[1]):] = False

    if not self.padder:
      return finger_mask
    else:
      w = self.padder.padding_width
      return finger_mask[w:-w,w:-w]


class WatershedMask(Masker):
  """Estimates the finger region given an input NIR image using Watershedding

  This method uses the `Watershedding Morphological Algorithm
  <https://en.wikipedia.org/wiki/Watershed_(image_processing)>` for determining
  the finger mask given an input image.

  The masker works first by determining image edges using a simple 2-D Sobel
  filter. The next step is to determine markers in the image for both the
  finger region and background. Markers are set on the image by using a
  pre-trained feed-forward neural network model (multi-layer perceptron or MLP)
  learned from existing annotations. The model is trained in a separate
  program and operates on 3x3 regions around the pixel to be predicted for
  finger/background. The ``(y,x)`` location also is provided as input to the
  classifier. The feature vector is then composed of 9 pixel values plus the
  ``y`` and ``x`` (normalized) coordinates of the pixel. The network then
  provides a prediction that depends on these input parameters. The closer the
  output is to ``1.0``, the more likely it is from within the finger region.

  Values output by the network are thresholded in order to remove uncertain
  markers. The ``threshold`` parameter is configurable.

  A series of morphological opening operations is used to, given the neural net
  markers, remove noise before watershedding the edges from the Sobel'ed
  original image.


  Parameters:

    model (str): Path to the model file to be used for generating
      finger/background markers. This model should be pre-trained using a
      separate program.

    foreground_threshold (float): Threshold given a logistic regression output
      (interval :math:`[0, 1]`) for which we consider finger markers provided
      by the network.  The higher the value, the more selective the algorithm
      will be and the less (foreground) markers will be used from the network
      selection. This value should be a floating point number in the open-set
      interval :math:`(0.0, 1.0)`.  If ``background_threshold`` is not set,
      values for background selection will be set to :math:`1.0-T`, where ``T``
      represents this threshold.

    background_threshold (float): Threshold given a logistic regression output
      (interval :math:`[0, 1]`) for which we consider finger markers provided
      by the network.  The smaller the value, the more selective the algorithm
      will be and the less (background) markers will be used from the network
      selection. This value should be a floating point number in the open-set
      interval :math:`(0.0, 1.0)`.  If ``foreground_threshold`` is not set,
      values for foreground selection will be set to :math:`1.0-T`, where ``T``
      represents this threshold.


  """


  def __init__(self, model, foreground_threshold, background_threshold):

    import bob.io.base
    import bob.learn.mlp
    import bob.learn.activation

    self.labeller = bob.learn.mlp.Machine((11,10,1))
    h5f = bob.io.base.HDF5File(model)
    self.labeller.load(h5f)
    self.labeller.output_activation = bob.learn.activation.Logistic()
    del h5f

    # adjust threshold from background and foreground
    if foreground_threshold is None and background_threshold is not None:
      foreground_threshold = 1 - background_threshold
    if background_threshold is None and foreground_threshold is not None:
      background_threshold = 1 - foreground_threshold
    if foreground_threshold is None and background_threshold is None:
      foreground_threshold = 0.5
      background_threshold = 0.5

    self.foreground_threshold = foreground_threshold
    self.background_threshold = background_threshold


  class _filterfun(object):
    '''Callable for filtering the input image with marker predictions'''


    def __init__(self, image, labeller):
      self.labeller = labeller
      self.features = numpy.zeros(self.labeller.shape[0], dtype='float64')
      self.output = numpy.zeros(self.labeller.shape[-1], dtype='float64')

      # builds indexes before hand, based on image dimensions
      idx = numpy.mgrid[:image.shape[0], :image.shape[1]]
      self.indexes = numpy.array([idx[0].flatten(), idx[1].flatten()],
          dtype='float64')
      self.indexes[0,:] /= image.shape[0]
      self.indexes[1,:] /= image.shape[1]
      self.current = 0


    def __call__(self, arr):

      self.features[:9] = arr.astype('float64')/255
      self.features[-2:] = self.indexes[:,self.current]
      self.current += 1
      return self.labeller(self.features, self.output)


  def run(self, image):
    '''Fully preprocesses the input image and returns intermediate results

      Parameters:

        image (numpy.ndarray): A 2D numpy array of type ``uint8`` with the
          input image


      Returns:

        numpy.ndarray: A 2D numpy array of type ``uint8`` with the markers for
        foreground and background, selected by the neural network model

        numpy.ndarray: A 2D numpy array of type ``float64`` with the edges used
        to define the borders of the watermasking process

        numpy.ndarray: A 2D numpy array of type boolean with the caculated
        mask. ``True`` values correspond to regions where the finger is
        located

    '''

    # applies the pre-trained neural network model to get predictions about
    # finger/background regions
    function = WatershedMask._filterfun(image, self.labeller)
    predictions = numpy.zeros(image.shape, 'float64')
    scipy.ndimage.filters.generic_filter(image, function,
        size=3, mode='nearest', output=predictions)

    selector = skimage.morphology.disk(radius=5)

    # applies a morphological "opening" operation
    # (https://en.wikipedia.org/wiki/Opening_(morphology)) to remove outliers
    markers_bg = numpy.where(predictions<self.background_threshold, 1, 0)
    markers_bg = skimage.morphology.opening(markers_bg, selem=selector)
    markers_fg = numpy.where(predictions>=self.foreground_threshold, 255, 0)
    markers_fg = skimage.morphology.opening(markers_fg, selem=selector)

    # avoids markers on finger borders
    selector = skimage.morphology.disk(radius=2)
    markers_fg = skimage.morphology.erosion(markers_fg, selem=selector)

    # the final markers are a combination of foreground and background markers
    markers = markers_fg | markers_bg

    # this will determine the natural boundaries in the image where the
    # flooding will be limited - dialation is applied on the output of the
    # Sobel filter to well mark the finger boundaries
    edges = skimage.filters.sobel(image)
    edges = skimage.morphology.dilation(edges, selem=selector)

    # applies watersheding to get a final estimate of the finger mask
    segmentation = skimage.morphology.watershed(edges, markers)

    # removes small perturbations and makes the finger region more uniform
    segmentation[segmentation==1] = 0
    mask = skimage.morphology.binary_opening(segmentation.astype('bool'),
        selem=selector)

    return markers, edges, mask


  def __call__(self, image):
    '''Inputs an image, returns a mask (numpy boolean array)

      Parameters:

        image (numpy.ndarray): A 2D numpy array of type ``uint8`` with the
          input image


      Returns:

        numpy.ndarray: A 2D numpy array of type boolean with the caculated
        mask. ``True`` values correspond to regions where the finger is
        located

    '''

    markers, edges, mask = self.run(image)
    return mask
