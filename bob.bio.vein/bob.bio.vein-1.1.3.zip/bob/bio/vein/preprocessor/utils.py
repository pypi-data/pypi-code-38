#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Utilities for preprocessing vein imagery"""

import numpy


def assert_points(area, points):
  """Checks all points fall within the determined shape region, inclusively

  This assertion function, test all points given in ``points`` fall within a
  certain area provided in ``area``.


  Parameters:

    area (tuple): A tuple containing the size of the limiting area where the
      points should all be in.

    points (numpy.ndarray): A 2D numpy ndarray with any number of rows (points)
      and 2 columns (representing ``y`` and ``x`` coordinates respectively), or
      any type convertible to this format. This array contains the points that
      will be checked for conformity. In case one of the points doesn't fall
      into the determined area an assertion is raised.


  Raises:

    AssertionError: In case one of the input points does not fall within the
      area defined.

  """

  for k in points:
    assert 0 <= k[0] < area[0] and 0 <= k[1] < area[1], \
        "Point (%d, %d) is not inside the region determined by area " \
        "(%d, %d)" % (k[0], k[1], area[0], area[1])


def fix_points(area, points):
  """Checks/fixes all points so they fall within the determined shape region

  Points which are lying outside the determined area will be brought into the
  area by moving the offending coordinate to the border of the said area.


  Parameters:

    area (tuple): A tuple containing the size of the limiting area where the
      points should all be in.

    points (numpy.ndarray): A 2D :py:class:`numpy.ndarray` with any number of
      rows (points) and 2 columns (representing ``y`` and ``x`` coordinates
      respectively), or any type convertible to this format. This array
      contains the points that will be checked/fixed for conformity. In case
      one of the points doesn't fall into the determined area, it is silently
      corrected so it does.


  Returns:

    numpy.ndarray: A **new** array of points with corrected coordinates

  """

  retval = numpy.array(points).copy()

  retval[retval<0] = 0 #floor at 0 for both axes
  y, x = retval[:,0], retval[:,1]
  y[y>=area[0]] = area[0] - 1
  x[x>=area[1]] = area[1] - 1

  return retval


def poly_to_mask(shape, points):
  """Generates a binary mask from a set of 2D points


  Parameters:

    shape (tuple): A tuple containing the size of the output mask in height and
      width, for Bob compatibility ``(y, x)``.

    points (list): A list of tuples containing the polygon points that form a
      region on the target mask. A line connecting these points will be drawn
      and all the points in the mask that fall on or within the polygon line,
      will be set to ``True``. All other points will have a value of ``False``.


  Returns:

    numpy.ndarray: A 2D numpy ndarray with ``dtype=bool`` with the mask
    generated with the determined shape, using the points for the polygon.

  """
  from PIL import Image, ImageDraw

  # n.b.: PIL images are (x, y), while Bob shapes are represented in (y, x)!
  mask = Image.new('L', (shape[1], shape[0]))

  # converts whatever comes in into a list of tuples for PIL
  fixed = tuple(map(tuple, numpy.roll(fix_points(shape, points), 1, 1)))

  # draws polygon
  ImageDraw.Draw(mask).polygon(fixed, fill=255)

  return numpy.array(mask, dtype=numpy.bool)


def mask_to_image(mask, dtype=numpy.uint8):
  """Converts a binary (boolean) mask into an integer or floating-point image

  This function converts a boolean binary mask into an image of the desired
  type by setting the points where ``False`` is set to 0 and points where
  ``True`` is set to the most adequate value taking into consideration the
  destination data type ``dtype``. Here are support types and their ranges:

    * numpy.uint8: ``[0, (2^8)-1]``
    * numpy.uint16: ``[0, (2^16)-1]``
    * numpy.uint32: ``[0, (2^32)-1]``
    * numpy.uint64: ``[0, (2^64)-1]``
    * numpy.float32: ``[0, 1.0]`` (fixed)
    * numpy.float64: ``[0, 1.0]`` (fixed)
    * numpy.float128: ``[0, 1.0]`` (fixed)

  All other types are currently unsupported.


  Parameters:

    mask (numpy.ndarray): A 2D numpy ndarray with boolean data type, containing
      the mask that will be converted into an image.

    dtype (numpy.dtype): A valid numpy data-type from the list above for the
      resulting image


  Returns:

    numpy.ndarray: With the designated data type, containing the binary image
    formed from the mask.


  Raises:

    TypeError: If the type is not supported by this function

  """

  dtype = numpy.dtype(dtype)
  retval = mask.astype(dtype)

  if dtype in (numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64):
    retval[retval == 1] = numpy.iinfo(dtype).max

  elif dtype in (numpy.float32, numpy.float64, numpy.float128):
    pass

  else:
    raise TypeError("Data type %s is unsupported" % dtype)

  return retval


def show_image(image):
  """Shows a single image using :py:meth:`PIL.Image.Image.show`

  .. warning::

     This function opens a new window. You must be operating interactively in a
     windowing system for it to work properly.

  Parameters:

    image (numpy.ndarray): A 2D numpy.ndarray compose of 8-bit unsigned
      integers containing the original image

  """

  from PIL import Image
  img = Image.fromarray(image)
  img.show()


def draw_mask_over_image(image, mask, color='red'):
  """Plots the mask over the image of a finger, for debugging purposes

  Parameters:

    image (numpy.ndarray): A 2D numpy.ndarray compose of 8-bit unsigned
      integers containing the original image

    mask (numpy.ndarray): A 2D numpy.ndarray compose of boolean values
      containing the calculated mask


  Returns:

    PIL.Image: An image in PIL format

  """

  from PIL import Image

  img = Image.fromarray(image).convert(mode='RGBA')
  msk = Image.fromarray((~mask).astype('uint8')*80)
  red = Image.new('RGBA', img.size, color=color)
  img.paste(red, mask=msk)

  return img


def show_mask_over_image(image, mask, color='red'):
  """Plots the mask over the image of a finger using :py:meth:`PIL.Image.Image.show`

  .. warning::

     This function opens a new window. You must be operating interactively in a
     windowing system for it to work properly.

  Parameters:

    image (numpy.ndarray): A 2D numpy.ndarray compose of 8-bit unsigned
      integers containing the original image

    mask (numpy.ndarray): A 2D numpy.ndarray compose of boolean values
      containing the calculated mask

  """

  draw_mask_over_image(image, mask, color).show()


def jaccard_index(a, b):
  """Calculates the intersection over union for two masks

  This function calculates the Jaccard index:

  .. math::

     J(A,B) &= \\frac{|A \cap B|}{|A \\cup B|} \\\\
            &= \\frac{|A \cap B|}{|A|+|B|-|A \\cup B|}


  Parameters:

    a (numpy.ndarray): A 2D numpy array with dtype :py:obj:`bool`

    b (numpy.ndarray): A 2D numpy array with dtype :py:obj:`bool`


  Returns:

    float: The floating point number that corresponds to the Jaccard index. The
    float value lies inside the interval :math:`[0, 1]`. If ``a`` and ``b`` are
    equal, then the similarity is maximum and the value output is ``1.0``. If
    the areas are exclusive, then the value output by this function is ``0.0``.

  """

  return (a & b).sum().astype(float) / (a | b).sum().astype(float)


def intersect_ratio(a, b):
  """Calculates the intersection ratio between the ground-truth and a probe

  This function calculates the intersection ratio between a ground-truth mask
  (:math:`A`; probably generated from an annotation) and a probe mask
  (:math:`B`), returning the ratio of overlap when the probe is compared to the
  ground-truth data:

  .. math::

     R(A,B) = \\frac{|A \\cap B|}{|A|}

  So, if the probe occupies the entirety of the ground-truth data, then the
  output of this function is ``1.0``, otherwise, if areas are exclusive, then
  this function returns ``0.0``. The output of this function should be analyzed
  against the output of :py:func:`intersect_ratio_of_complement`, which
  provides the complementary information about the intersection of the areas
  being analyzed.


  Parameters:

    a (numpy.ndarray): A 2D numpy array with dtype :py:obj:`bool`, that
      corresponds to the **ground-truth object**

    b (numpy.ndarray): A 2D numpy array with dtype :py:obj:`bool`, that
      corresponds to the probe object that will be compared to the ground-truth


  Returns:

    float: The floating point number that corresponds to the overlap ratio. The
    float value lies inside the interval :math:`[0, 1]`.

  """

  return (a & b).sum().astype(float) / a.sum().astype(float)


def intersect_ratio_of_complement(a, b):
  """Calculates the intersection ratio between the complement of ground-truth and a probe

  This function calculates the intersection ratio between *the complement* of a
  ground-truth mask (:math:`A`; probably generated from an annotation) and a
  probe mask (:math:`B`), returning the ratio of overlap when the probe is
  compared to the ground-truth data:

  .. math::

     R(A,B) = \\frac{|A^c \\cap B|}{|A|} = B \\setminus A


  So, if the probe is totally inside the ground-truth data, then the output of
  this function is ``0.0``, otherwise, if areas are exclusive for example, then
  this function outputs greater than zero. The output of this function should
  be analyzed against the output of :py:func:`intersect_ratio`, which provides
  the complementary information about the intersection of the areas being
  analyzed.

  Parameters:

    a (numpy.ndarray): A 2D numpy array with dtype :py:obj:`bool`, that
      corresponds to the **ground-truth object**

    b (numpy.ndarray): A 2D numpy array with dtype :py:obj:`bool`, that
      corresponds to the probe object that will be compared to the ground-truth


  Returns:

    float: The floating point number that corresponds to the overlap ratio
    between the probe area and the *complement* of the ground-truth area.
    There are no bounds for the float value on the right side:
    :math:`[0, +\\infty)`.

  """

  return ((~a) & b).sum().astype(float) / a.sum().astype(float)
