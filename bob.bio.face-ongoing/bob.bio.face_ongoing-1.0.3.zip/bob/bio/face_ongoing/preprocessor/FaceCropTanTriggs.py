#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Thu May 24 10:41:42 CEST 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bob.ip.base
import bob.ip.color
import numpy

from bob.bio.face.preprocessor import FaceCrop

class FaceCropTanTriggs (FaceCrop):
  """Crops the face according to the given annotations in the same fashing as in :py:class:`bob.bio.face.preprocessor.FaceCrop` 
  and it returns either a 4 channel crop (RGB + TanTriggs) or 2 channel crop (Gray scale + TanTriggs)


  **Parameters:**

  cropped_image_size : (int, int)
    The size of the resulting cropped images.

  cropped_positions : dict
    The coordinates in the cropped image, where the annotated points should be put to.
    This parameter is a dictionary with usually two elements, e.g., ``{'reye':(RIGHT_EYE_Y, RIGHT_EYE_X) , 'leye':(LEFT_EYE_Y, LEFT_EYE_X)}``.
    However, also other parameters, such as ``{'topleft' : ..., 'bottomright' : ...}`` are supported, as long as the ``annotations`` in the `__call__` function are present.

  fixed_positions : dict or None
    If specified, ignore the annotations from the database and use these fixed positions throughout.

  mask_sigma : float or None
    Fill the area outside of image boundaries with random pixels from the border, by adding noise to the pixel values.
    To disable extrapolation, set this value to ``None``.
    To disable adding random noise, set it to a negative value or 0.

  mask_neighbors : int
    The number of neighbors used during mask extrapolation.
    See :py:func:`bob.ip.base.extrapolate_mask` for details.

  mask_seed : int or None
    The random seed to apply for mask extrapolation.

    .. warning::
       When run in parallel, the same random seed will be applied to all parallel processes.
       Hence, results of parallel execution will differ from the results in serial execution.

  kwargs
    Remaining keyword parameters passed to the :py:class:`Base` constructor, such as ``color_channel`` or ``dtype``.
  """

  def __init__(
      self,
      cropped_image_size,        # resolution of the cropped image, in order (HEIGHT,WIDTH); if not given, no face cropping will be performed
      cropped_positions,         # dictionary of the cropped positions, usually: {'reye':(RIGHT_EYE_Y, RIGHT_EYE_X) , 'leye':(LEFT_EYE_Y, LEFT_EYE_X)}
      fixed_positions = None,    # dictionary of FIXED positions in the original image; if specified, annotations from the database will be ignored
      mask_sigma = None,         # The sigma for random values areas outside image
      mask_neighbors = 5,        # The number of neighbors to consider while extrapolating
      mask_seed = None,          # The seed for generating random values during extrapolation
      color_channel="rgb",
      **kwargs                   # parameters to be written in the __str__ method
  ):

    # call base class constructor
    FaceCrop.__init__(
        self,
        cropped_image_size = cropped_image_size,
        cropped_positions = cropped_positions,
        fixed_positions = fixed_positions,
        mask_sigma = mask_sigma,
        mask_neighbors = mask_neighbors,
        mask_seed = mask_seed,
        color_channel=color_channel
    )
    
    self.tantriggs = bob.ip.base.TanTriggs()


  def __call__(self, image, annotations = None):
    """__call__(image, annotations = None) -> face

    Aligns the given image according to the given annotations.

    First, the desired color channel is extracted from the given image.
    Afterward, the face is cropped, according to the given ``annotations`` (or to ``fixed_positions``, see :py:meth:`crop_face`).
    Finally, the resulting face is converted to the desired data type.

    **Parameters:**

    image : 2D or 3D :py:class:`numpy.ndarray`
      The face image to be processed.

    annotations : dict or ``None``
      The annotations that fit to the given image.

    **Returns:**

    face : 2D :py:class:`numpy.ndarray`
      The cropped face.
    """
    
    def normalize(img):
      return (255 * ((img - numpy.min(img)) / (numpy.max(img)-numpy.min(img))))

    # convert to the desired color channel
    image = self.color_channel(image)
    # crop face
    image = self.crop_face(image, annotations)

    if image.shape[0] == 3:
        tt_image = normalize(self.tantriggs(bob.ip.color.rgb_to_gray(image.astype("uint8"))))
    else:
        tt_image = normalize(self.tantriggs(image))
        image = numpy.reshape(image, (1, image.shape[0], image.shape[1]))

    tt_image = numpy.reshape(tt_image, (1, tt_image.shape[0], tt_image.shape[1]))
    image = numpy.vstack((image, tt_image))
    
    # convert data type
    return self.data_type(image)

