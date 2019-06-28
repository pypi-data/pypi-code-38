# Copyright (C) 2018-2019 The Plenpy Authors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Module defining the :class:`plenpy.lightfields.LightField` class.

"""

import gc
import os
import sys

import imageio
import matplotlib.pyplot as plt
import matplotlib.colors
from numpy.core.multiarray import ndarray
import numpy as np
from scipy import interpolate
from scipy.interpolate import RegularGridInterpolator as RGI
from scipy.ndimage.filters import gaussian_filter
import skimage
import skimage.color
import skimage.transform
from typing import List, Optional, Union, Tuple, Type
from tkinter import TclError

import plenpy.logg

from plenpy.utilities import core
from plenpy import spectral
from plenpy.utilities import denoise
from plenpy.utilities import images
from plenpy.utilities import kernels
from plenpy.utilities.misc import get_avail_extensions
from plenpy.utilities import colors

logger = plenpy.logg.get_logger()

_all_ = ['LightField']

# Here, prefer the FreeImage plugin over PIL to be able to read 16bit data
imageio.formats.sort('-FI', '-PIL')


class LightField(core.SpectralArray):
    """LightField class representing a (spectral) light field.

    This class is derived from the core
    :class:`core.SpectralArray` class.

    This class is mostly equivalent to the
    :class:`core.SpectralArray` class but restricts the
    number of dimensions to 5 exactly, i.e. it will always be of shape
    (u, v, s, t, num_channels). It then extends its parent class by some
    useful methods specific to light fields as well as multiple
    methods to create/read/show a light field.

    See Also:
        See the parent class :class:`core.SpectralArray`
        for the basic Attributes.

    Notes:
        Basically, a lightfield is represented as a 5 dimensional
        class:`numpy.ndarray` L(u, v, s, t, num_channels), where
        (u, v) and (s, t) correspond to the intersection of the light rays
        with two planes (plane-plane parametrization of the light field),
        e.g. corresponding to the main lens plane and the microlens array
        plane of a camera.

        The implementation works with monochromatic, as well as RGB or even
        hyperspectral light fields, corresponding to num_channels = 1, 3, >3 .

        This class implements different classmethods to initialize a light field
        object for example from a 4 or 5 dimensional :class:`numpy.ndarray` or,
        more conveniently, from image data. For example, a light field could be
        saved as a collection of subaperture views in one or multiple images.

        Furthermore, the class implements many routines to manipulate or evaluate
        light fields, such as calculation of epipolar images, depth estimation or
        refocus methods. Also, the class provides methods to visualize the
        light field data, for example by an interactive subaperture visualization
        or two dimensional rearrangements of the lightfield, e.g. as
        a collection of subapertures.
    """

    def __new__(cls, *args, **kwargs) -> 'LightField':
        """See Also: :class:`core.SpectralArray`
        """
        # Set ndim_exp=5, everything else is done in SpectralArray class.
        return super().__new__(cls,*args, **kwargs, ndim_exp=5)

    @staticmethod
    def _4d_to_2d(data: ndarray) -> ndarray:
        """Calculate the 2D representation of a 4D light field.

        That is, calculate a collection of subaperture views.
        The Lightfield L(u,v,s,t) is rewritten to
        I(a,b) with subapertures L(u, v, :, :) for u, v = 0,1,2,...

        Args:
            data: A numpy array representing the light field data, e.g.
            a LightField._data member, of shape (u, v, s, t, num_channels).

        Returns:
            A 2D representation of the lightfield, i.e.
            a numpy array of shape (u*s, v*t, num_channels).
            A copy is returned, not a view.

        See Also:
             The inverse function :func:`_2d_to_4d`.

        """
        u_max, v_max, s_max, t_max, num_channels = data.shape
        a = u_max * s_max
        b = v_max * t_max

        return data.swapaxes(1, 2).reshape(a, b, num_channels)

    @staticmethod
    def _2d_to_4d(data: ndarray,
                  s_max: int,
                  t_max: Optional[int] = None) -> ndarray:
        """Calculate a light field from a 2D representation.

        That is, calculate the 4D light field from a collection
        of subaperture views. See also :func:`_4d_to_2d`


        Args:
            data: The 2D subaperture collection data, e.g. a
                  numpy array of shape (u_max*s_max, v_max*t_max, num_channels).

            s_max: Height of each subaperture.

            t_max: Width of each subaperture.
                   Default value is equal to ``sub_height``.

        Returns:
            A 4D representation of the light field, i.e.
            a numpy array of shape (u_max, v_max, s_max, t_max, num_channels).
            A copy is returned, not a view.

        See Also:
            The inverse function :func:`_4d_to_2d`.
        """

        if t_max is None:
            t_max = s_max

        if data.ndim == 2:
            data = data[..., np.newaxis]

        a_max, b_max, num_channels = data.shape

        # Calculate lf indices
        u_max = a_max // s_max
        v_max = b_max // t_max

        # Check consistency:
        if not (a_max == s_max * u_max and b_max == t_max * v_max):
            raise ValueError("Inconsistent data dimensions. "
                             "Check if sub_width and sub_height are "
                             "specified correctly.")

        return data.reshape(u_max, s_max, v_max, t_max,
                            num_channels).swapaxes(1, 2)

    @classmethod
    def from_img_data(cls,
                      img: ndarray,
                      s_max: int,
                      t_max: Optional[int] = None,
                      **kwargs) -> 'LightField':
        """Initialize a LightField from a single image.

        The image stores the lightfield as a 2D subaperture view collection.

        Args:
            img: The light field data as 2D image of a subaperture view
                collection with shape (u_max*s_max, v_max*t_max, num_channels)
                or (u_max*s_max, v_max*t_max).

            s_max: Height of each subaperture.

            t_max: Width of each subaperture.

            **kwargs : See :class:`core.SpectralArray`
        """
        logger.info("Reading lightfield from 2D image data ...")

        if t_max is None:
            t_max = s_max

        # Calculate 4D data from 2D representation
        data = LightField._2d_to_4d(data=img,
                                    s_max=s_max,
                                    t_max=t_max)

        # Return LightField object initialized from numpy data.
        logger.info("...done")
        return cls(data, **kwargs)

    @classmethod
    def from_file(cls,
                  path: str,
                  s_max: int,
                  t_max: Optional[int] = None,
                  format: Optional[str] = None,
                  **kwargs) -> 'LightField':
        """Initialize a LightField from a single image file path.

        The image stores the lightfield as a 2D subaperture view collection.

        Args:
            path: Image file system path.

            s_max: Height of each subaperture.

            t_max: Width of each subaperture.
                   Default value is equal to ``sub_height``.

            format: Image format.
                By default, imageio selects an appropriate one based
                on the filename and its contents.
                Use :func:`plenpy.utilities.misc.get_avail_extensions()`
                to get a list of available formats.

            **kwargs : See :class:`core.SpectralArray`
        """

        logger.info(f"Reading light field from file {path} ...")

        # First, read spectral image from data
        hsi = spectral.SpectralImage.from_file(path=path, format=format)

        # Return LightField object initialized from img data.
        logger.info("...done")
        return cls.from_img_data(img=hsi, s_max=s_max, t_max=t_max,
                                 **kwargs)

    @classmethod
    def from_file_mask(cls,
                       img_path: str,
                       mask_path: str,
                       format: Optional[str] = None,
                       **kwargs) -> 'LightField':
        """Initialize a LightField from a single masked image file.

         The light field is stored as a 2D image of a subaperture
         view collection. The color mask defines which color channel the
         image light field's pixel belongs to (color coded light field).

        Args:
            img_path: System path to the lightfield image file.

            mask_path: System path to the mask npy file.

            format: Image format.
                By default, imageio selects an appropriate one based
                on the filename and its contents.
                Use :func:`plenpy.utilities.misc.get_avail_extensions()`
                to get a list of available formats.

            **kwargs : See :class:`core.SpectralArray`
        """
        mask = np.load(mask_path).astype(float)
        # Set zero values to nan, s.t. they are masked in the lightfield
        np.place(mask, mask == 0, np.nan)
        s, t, num_channels = mask.shape

        # Load local image
        # convert the image to greyscale
        img = imageio.imread(os.path.abspath(img_path), format)
        dtype_ = img.dtype

        # Convert to float, since NANs are not applicable else
        img = skimage.img_as_float64(img)

        # Convert to greyscale
        img = (skimage.color.rgb2gray(img))

        if img.ndim == 2:
            img = img[..., np.newaxis]

        a, b, num_img_channels = img.shape
        u = a//s
        v = b//t

        # Check dimension consistency
        if not (a == u * s and b == v * t):
            raise ValueError("The mask and image shapes are incompatible.")

        # Apply mask to img and create light field
        return cls.from_img_data(np.tile(mask, (u, v, 1))*img, s, t, **kwargs)

    @classmethod
    def from_file_collection(cls,
                             path: str,
                             u_max: int,
                             v_max: Optional[int] = None,
                             invert: Optional[str] = None,
                             format: Optional[str] = None,
                             **kwargs) -> 'LightField':
        """Initialize a LightField from multiple image files.
        
        Each image corresponds to a subaperture view of the light field.

        Args:
            path: System path to folder containing the subaperture view images.
                The folder must not contain any other image data.

            u_max: Size of the light field in u-direction. This corresponds to
                the number of subparture images in u-direction.

            v_max: Size of the light field in v-direction. This corresponds to
                the number of subparture images in v-direction.
                If no value is given, a square light field is assumed ,
                i.e. ``v_max = u_max``.

            format: Image format.
                By default, imageio selects an appropriate one based
                on the filename and its contents.
                Use :func:`plenpy.utilities.misc.get_avail_extensions()`
                to get a list of available formats.

            **kwargs: See :class:`core.SpectralArray`

        Note:
            If you want to load a spectral LightField that is saved in a
            2D representation channel wise, use :class:`spectral.SpectralImage`
            to load the spectral data and the
            :func:`LightField.from_img_data()` to convert to a LightField.

        """
        logger.info(f"Reading light field from folder {path} ...")

        if v_max is None:
            v_max = u_max

        image_paths = []
        for file in os.listdir(path):
            # Check that the file is a readable image file
            for extension in get_avail_extensions():
                if file.lower().endswith(extension) and \
                        not file.lower().endswith('.npz'):
                    image_paths.append(os.path.join(path, file))

        # Sort list alphanumerically
        image_paths.sort()

        # Check that num_u * num_v images have been found
        if not len(image_paths) == u_max*v_max:
            raise ValueError(f"Found {len(image_paths)} images. "
                             f"Expected {u_max*v_max}. Please check that all "
                             f"images in the folder are readable.")

        # Read the images and check that they are of same shape
        image_list = []
        for file in image_paths:
            image_list.append(
                np.asarray(imageio.imread(os.path.abspath(file), format)))

        shape = image_list[0].shape
        for image in image_list:
            if not image.shape == shape:
                raise ValueError(f"The images are not all of the same shape.")

        # Ready to put images together to light field data
        # Convert list to np ndarray
        image_list = np.asarray(image_list)

        # Caution: usually the images are sorted in ascending v-direction first
        if len(shape) == 2:
            # when images are black and white, add third axis (without copy)
            image_list = image_list[..., np.newaxis]

        shape = image_list[0].shape
        s, t, num_channels = shape
        logger.info("...done")

        # Invert u ordering
        if invert == 'u':
            return cls(np.flip(image_list.reshape(u_max, v_max, s, t, num_channels), axis=0),
                       **kwargs)
        # Invert v ordering
        elif invert == 'v':
            return cls(np.flip(image_list.reshape(u_max, v_max, s, t, num_channels), axis=1),
                       **kwargs)

        # Invert u and v ordering
        elif invert == 'both':
            return cls(np.flip(np.flip(image_list.reshape(u_max, v_max, s, t, num_channels), axis=0), axis=1),
                       **kwargs)

        elif invert is None:
            return cls(image_list.reshape(u_max, v_max, s, t, num_channels),
                       **kwargs)

        else:
            raise ValueError(f"Invert {invert} not valid.")

    def save(self,
             path: str,
             name: str = "image",
             ext: str = '.png',
             dtype: Union[np.uint8, np.uint16] = np.uint8):
        """ Save the light field as a 2D image.

        To save as a numpy array, use Numpy's :func:`numpy.save()` function
        instead. To save a RGB image, use :func:`save_rgb()`.

        The 2D image corresponds to the collection of subaperture views.
        See also :func:`._4d_to_2d()`. If more than 3 color channels are found,
        every color channel is saved separately, otherwise a RGB image is
        saved.

        Args:
            path: System folder path to save the image.
                  Both absolute or relative image paths allowed.

            name: Image basename. Channel number and extension will be appended.

            ext: Extension of target image.

            dtype: Target dtype. Either uint8 or uint16.

        """
        logger.info(f"Saving light field to {path}...")

        # Create HSI from 2D representation of light field
        hsi = spectral.SpectralImage(LightField._4d_to_2d(self))

        # Save HSI
        hsi.save(path=path)

        logger.info("...done")
        return

    def save_rgb(self, path: str):
        """ Save the light field as a 2D RGB image.

        To save as a numpy array, use Numpy's :func:`numpy.save()` function
        instead. To save a RGB image, use :func:`save_rgb()`.

        The 2D image corresponds to the collection of subaperture views.
        See also :func:`._4d_to_2d()`. If more than 3 color channels are found,
        every color channel is saved separately, otherwise a RGB image is
        saved.

        Args:
            path: System path to save the image.
                Both absolute or relative image paths allowed.

        """
        logger.info(f"Saving light field to {path}...")

        # Create HSI from 2D representation of light field
        hsi = spectral.SpectralImage(LightField._4d_to_2d(self))

        # Save HSI
        hsi.save_rgb(path=path)

        logger.info("...done")
        return

    def get_subaperture(self,
                        u: int,
                        v: int,
                        copy: bool = True) -> ndarray:
        """Get a subaperture view of the light field.

        Args:
            u: Fixed u-coordinate of the subaperture view.

            v: Fixed v-coordinate of the subaperture view.

            copy: Flag indicating whether a copy or a ndarray view is returned.
                Default is to return a copy.

        Returns:
            Subaperture of shape (s_max, t_max, num_channels).

        """
        if copy:
            return self[u, v, :, :, :].copy()
        else:
            return self[u, v, :, :, :]

    def calc_epi(self,
                 axis: int,
                 coordinate: int,
                 sub_coordinate: int) -> ndarray:
        """Calulate an epipolar image of a light field.

        Args:
            axis: Axis along the epipolar image is calculated.
                ``axis = 0`` corresponds to axis along the u-direction,
                ``axis = 1`` corresponds to axis along the v-direction.

            coordinate: Main coordinate for which to calculate the
                epipolar image.
                If ``axis = 0``, defines which v-coordinate to fix,
                If ``axis = 1``, defines which to u-coordinate to fix.

            sub_coordinate: Sub_coordinate for which to calculate the
                epipolar image.
                If ``axis = 0``, defines which s-coordinate to fix,
                If ``axis = 1``, defines which t-coordinate to fix.

        Returns:
            Epipolar image of the given coordinates along the specified axis.

        """

        # Calculate size of output image
        if axis == 0:
            # Calculate epi
            result = self[:, coordinate, :, sub_coordinate]
            # Axes have to be swapped because
            # result[a,b] = data[b, coordinate, a, subcoordinate]
            # but the : operator causes to iterates b first so we get
            # result[b,a] which we have to transpose.
            result = np.swapaxes(result, 0, 1)

        elif axis == 1:
            # Calculate epi
            result = self[coordinate, :, sub_coordinate, :]

        else:
            raise ValueError(f"Illegal axis {axis} specified. "
                             "Axis must be 0 or 1.")

        return result.copy()

    def calc_2_5d_epi(self,
                      axis: int,
                      coordinate: int,
                      sub_coordinate: int,
                      sigma: float = 2.5) -> ndarray:
        """Calulate a 2.5D epipolar image of a light field.

        The difference to 2D EPIs is an additional smoothing step
        in u-direction or v-direction.
        A gaussian filter is used for smoothing.

        Args:
            axis: Axis along the epipolar image is calculated.
                ``axis = 0`` corresponds to axis along the u-direction,
                ``axis = 1`` corresponds to axis along the v-direction.

            coordinate: Main coordinate for which to calculate the
                epipolar image.
                If ``axis = 0``, defines which v-coordinate to fix,
                If ``axis = 1``, defines which to u-coordinate to fix.

            sub_coordinate: Sub_coordinate for which to calculate the
                epipolar image.
                If ``axis = 0``, defines which s-coordinate to fix,
                If ``axis = 1``, defines which t-coordinate to fix.

            sigma: Standard deviation for gaussian smoothing.

        Returns:
            Epipolar image of the given coordinates along the specified axis.

        """

        # Calculate size of output image
        if axis == 0:
            # Calculate epi-volume and filter over v-dimension
            epi_volume_filtered = gaussian_filter(
                np.squeeze(self[:, :, :, sub_coordinate]),
                sigma=(0, sigma, 0, 0))

            result = epi_volume_filtered[:, coordinate, :].swapaxes(0, 1)
            # Axes have to be swapped because
            # result[a,b] = data[b, coordinate, a, sub_coordinate]
            # but the : operator causes to iterates b first so we get
            # result[b,a] which we have to transpose.

        elif axis == 1:
            # Calculate epi-volume and filter over u-dimension
            epi_volume_filtered = gaussian_filter(
                np.squeeze(self[:, :, sub_coordinate, :]),
                sigma=(sigma, 0, 0, 0))
            result = epi_volume_filtered[coordinate, :, :]

        else:
            raise ValueError(f"Illegal axis {axis} specified. "
                             "Axis must be 0 or 1.")

        return result

    def epi_generator(self, method: str, axis: int, coordinate: int):
        """Generates EPIs for a fixed axis and a fixed angular coordinate.

        Yields a EPI for the different subcoordinates. That is,
        fixing an axis (u- or v- axis) and a coordinate (the u=const, v=const
        coordinate), iterates through the s- or t- coordinate as the subcoordinate
        and yields the corresponding epi.

        Args:
            method: Method used to calculate the EPI. Either:

                       * '2D': Use regular EPI, see :func:calc_epi()
                       * '2.5D': Use 2.5D EPI calculation via Gaussian filtering, see :func:calc_2_5d_epi()

            axis: Axis along which to calculate the EPI.

            coordinate: Angular coordinate to fix.

        Yields:
            Tuples (EPI, subcoordinate) of EPIs with succeeding subcoordinate

        """

        u, v, s, t, ch = self.shape
        n = 0

        method = method.lower()

        if method == '2d':
            get_epi = self.calc_epi
        elif method == '2.5d':
            get_epi = self.calc_2_5d_epi
        else:
            raise ValueError(f"Unknown method '{method}'.")

        if axis == 0:
            n_max = t

        elif axis == 1:
            n_max = s

        else:
            raise ValueError("Option 'axis' has to be 0 or 1.")

        while n < n_max:
            yield get_epi(axis=axis, coordinate=coordinate, sub_coordinate=n), n
            n += 1

    def get_colorcoded_copy(self,
                            method: Union[str, ndarray] = "random",
                            return_mask: bool = False) -> "LightField":
        """Return a color coded copy of the lightfield.

        Args:
            method: Mask or method that is to be used for color coding.
                A mask can be specified as a numpy array of
                shape (s_max, t_max, num_ch).
                Other availables methods are:\n
                    * 'random': Create a random mask using uniform
                        distribution for the chosen color index.

            return_mask: Boolean flag indicating whether to also return the
                used mask.

        Returns:
            A LightField object whose data is colorcoded using the specified
            method. Values are masked with np.nan to be distinguishable from
            zero values. If ``return_mask`` is True, the used mask is also
            returned, tuple wise.

        """
        u, v, s, t, num_ch = self.shape

        # Init mask with nans
        mask = np.nan * np.zeros((s, t, num_ch))

        if type(method) == str:
            if method == "random":

                # Draw a random wavelength channel for every s and t
                size = (s, t)
                ch = np.random.random_integers(0, num_ch - 1, size=size)

                a = np.repeat(np.arange(0, s), t)
                b = np.tile(np.arange(0, t), s)

                # Place ones into mask according to channel index
                mask[a, b, ch[a, b]] = 1.0
                del ch

            elif method == "regular":
                # Only works for quadratic number of channels
                sqrt = np.sqrt(num_ch)
                if not sqrt % 1 == 0:
                    raise ValueError(
                        f"Regular mask only works with square number of "
                        f"color channels. Found {num_ch}.")

                # Construct regular sqrt(num_ch) x sqrt(num_ch) filter mask
                size = (s, t)
                sqrt = int(sqrt)
                ch = np.arange(num_ch).reshape((sqrt, sqrt))

                # Expand ch to size (s, t)
                rep_s = 1 + s // sqrt
                rep_t = 1 + t // sqrt

                ch = np.tile(ch, (rep_s, rep_t))
                ch = ch[:s, :t]

                a = np.repeat(np.arange(0, s), t)
                b = np.tile(np.arange(0, t), s)

                # Place ones into mask according to channel index
                mask[a, b, ch[a, b]] = 1.0
                del ch

            else:
                raise ValueError(f"Unknown method: '{method}'.")

        elif type(method) == ndarray:
            shape = method.shape
            if not shape == (s, t, num_ch):
                raise ValueError(f"The given mask is of incompatibel shape.\n"
                                 f"Given: {shape}.\n"
                                 f"Expected: {(s, t, num_ch)}.")
            mask = method
            np.place(mask, mask == 0, np.nan)

        else:
            raise ValueError(f"Unknown method type: {type(method)}.")

        # Create full mask of light field size
        full_mask = np.repeat(mask[..., np.newaxis], u, axis=-1)
        full_mask = np.repeat(full_mask[..., np.newaxis], v, axis=-1)
        full_mask = full_mask.transpose((3, 4, 0, 1, 2))

        # Apply mask to light field data
        data = full_mask * self

        # Return new lightfield
        if return_mask:
            return LightField(data), mask
        else:
            return LightField(data)

    @staticmethod
    def _estimate_orientation_structure_tensor(
            epi: ndarray,
            grad_method: str = 'scharr') -> Tuple[ndarray, ndarray]:
        """Calculates orientation of an EPI-slice using the structure tensor.

        Orientation estimation is based on the analysis of structure tensor
        and its eigenvalues. Axis of input EPI-slice has to be in order
        (u, s) or (v, t). This implementation is based on [R5]_ with
        calculations from [R6]_.

        Args:
            epi: Epipolar image, i.e. a numpy array with shape
                (u, s) or (t, v).

            method: Method used for calculating image gradient.
                    See :func:`plenpy.utilities.images.get_gradients`.

        Returns:
            Tuple of numpy arrays containing

                - **disparity**: A numpy array of shape (s, 1) or (t, 1),
                  representing disparity.
                - **confidence**: A numpy array of shape (s, 1) or (t, 1),
                  representing confidence in the disparity estimation.
                  Higher means better.

        References:
            .. [R5]  S. Wanner,  B. Goldluecke (2014).
                Variational light field analysis for disparity
                estimation and super-resolution.
                IEEE Transactions on Pattern Analysis and Machine
                Intelligence 36 (3)
                DOI: 10.1109/TPAMI.2013.147
            .. [R6]  J. Bigün and G.H. Granlund (1987).
                Optimal Orientation Detection of
                Linear Symmetry.
                IEEE International Conference on Computer Vision
                pp. 433-438

        """

        # Parameters for fine tuning
        gauss_inner_scale = 0.75
        gauss_outer_scale = 2.0

        # Filter EPI to reduce noise
        epi = gaussian_filter(epi, gauss_inner_scale)

        # Get image gradients
        gx, gy = images.get_gradients(epi, method=grad_method)

        # Calculate Structure tensor: T = [Jxx,Jxy;Jxy,Jyy]
        # and filter elements
        Jxx = gaussian_filter(gx * gx, gauss_outer_scale)
        Jyy = gaussian_filter(gy * gy, gauss_outer_scale)
        Jxy = gaussian_filter(gx * gy, gauss_outer_scale)

        # Extract center line
        Jxx = Jxx[round((epi.shape[0] - 1) / 2.0), :]
        Jyy = Jyy[round((epi.shape[0] - 1) / 2.0), :]
        Jxy = Jxy[round((epi.shape[0] - 1) / 2.0), :]

        # Confidence of depth estimation
        confidence = np.where((Jxx + Jyy) < np.finfo(np.float64).eps,
                              0,
                              np.sqrt(((Jyy - Jxx) ** 2 + 4 * Jxy ** 2) / (
                                          Jxx + Jyy) ** 2))

        # Disparity (use eigenvector of structure tensor J)
        disparity = 0.5 * (Jxx - Jyy - np.sqrt((Jxx - Jyy) ** 2 + 4 * Jxy ** 2)) / Jxy

        return disparity, confidence

    def _get_disparity_structure_tensor(self, epi_method: str = '2d', **kwargs):
        """Calculates a depth map from the light field.

        The depth is calculated from the 4D representation
        L(u,v,s,t) using orientation estimation on the epipolar
        plane images.

        Args:
            epi_method: Method used for EPI calculation, see :func:epi_generator()

        Returns:
            Tuple of numpy arrays containing

                * ``disparity``:
                    A numpy array of shape (s, t), representing disparity.
                * ``confidence``:
                    A numpy array of shape (s, t), representing confidence in
                    the disparity estimation. Higher is better.

        See Also:
            The disparity is estimated using :func:_estimate_orientation_structure_tensor().

        """
        # Get shape
        u_max, v_max, s_max, t_max, num_ch = self.shape

        # Coordinates of center sub aperture image
        u_center = round((u_max - 1) / 2.0)
        v_center = round((v_max - 1) / 2.0)

        # Estimate disparity for epi slices along u-direction
        disparity_u = np.zeros((s_max, t_max, num_ch))
        confidence_u = np.zeros(disparity_u.shape)

        for epi_u, s in self.epi_generator(method=epi_method, axis=1, coordinate=u_center):
            # Iterate through color channels and estimate disparity
            for ch in range(0, num_ch):
                res = self._estimate_orientation_structure_tensor(
                    epi_u[..., ch].astype(np.float64), **kwargs)

                disparity_u[s, :, ch], confidence_u[s, :, ch] = res

        # Estimate disparity for epi slices along v-direction
        disparity_v = np.zeros((s_max, t_max, num_ch))
        confidence_v = np.zeros(disparity_v.shape)
        for epi_v, t in self.epi_generator(method=epi_method, axis=0, coordinate=v_center):
            # Swap axis so EPI is of shape (v, t)
            epi_v = np.swapaxes(epi_v, 0, 1)

            # Iterate through color channels and estimate disparity
            for ch in range(0, num_ch):
                res = self._estimate_orientation_structure_tensor(
                    epi_v[..., ch].astype(np.float64), **kwargs)

                disparity_v[:, t, ch], confidence_v[:, t, ch] = res

        # Set reliability of invalid pixels to minimum
        confidence_u[np.isnan(disparity_u) | np.isnan(confidence_u)] = 0
        confidence_v[np.isnan(disparity_v) | np.isnan(confidence_v)] = 0
        logger.info("...done")

        return -disparity_u, -disparity_v, confidence_u, confidence_v

    @staticmethod
    def _estimate_orientation_brute_force_2d(
            epi: ndarray,
            vmin: float, vmax: float,
            num_slopes: int = 40) -> Tuple[ndarray, ndarray]:
        """Calculates orientation of an EPI-slice using a brute force line fit.

        Args:
            epi: Grey scale Epipolar image, i.e. a numpy array with shape
                (u, s) or (t, v) such that the first axis is angular.

        Returns:
            Tuple of numpy arrays containing

                - **disparity**: A numpy array of shape (s, 1) or (t, 1),
                  representing disparity.
                - **confidence**: A numpy array of shape (s, 1) or (t, 1),
                  representing confidence in the disparity estimation.
                  Higher means better.

        """

        y, x = epi.shape
        sigma = 1.5

        slopes = np.linspace(vmin, vmax, num_slopes)

        variance = np.zeros((num_slopes, x))
        confidences = np.zeros((num_slopes, x))

        for i in range(num_slopes):
            # Shear image by slope and crop to central region
            im_sheared = images.shear(epi, slopes[i], order=1)
            im_sheared = gaussian_filter(im_sheared, [0, sigma])
            variance[i] = np.var(im_sheared, axis=0)

            # For confidence, use gradient (Sobel operator)
            g = images.get_edges(epi, method='scharr')
            confidences[i] = np.sum(np.abs(g), axis=0)

        # Get slope where variance is minimal
        disparity = -slopes[variance.argmin(axis=0)]
        confidence = confidences[np.where(variance == variance.min(axis=0))]

        return disparity, confidence

    def _get_disparity_brute_force_2d(self,
                                      epi_method: str = '2d',
                                      **kwargs):
        """Calculates a depth map from the light field using 2D brute force line fit.

        The depth is calculated from the 4D representation
        L(u,v,s,t) using brute force line fitting on the epipolar
        plane images.

        Returns:
            Tuple of numpy arrays containing

                * ``disparity``:
                    A numpy array of shape (s, t), representing disparity.
                * ``confidence``:
                    A numpy array of shape (s, t), representing confidence in
                    the disparity estimation. Higher is better.

        See Also:
            The disparity is estimated using :func:_estimate_orientation_2d_brute_force().

        """
        # Get shape
        u_max, v_max, s_max, t_max, num_ch = self.shape

        # Coordinates of center sub aperture image
        u_center = round((u_max - 1) / 2.0)
        v_center = round((v_max - 1) / 2.0)

        # Estimate disparity for epi slices along u-direction
        disparity_u = np.zeros((s_max, t_max, num_ch))
        confidence_u = np.zeros(disparity_u.shape)

        for epi_u, s in self.epi_generator(method=epi_method, axis=1,
                                           coordinate=u_center):
            # Iterate through color channels and estimate disparity
            for ch in range(0, num_ch):
                res = self._estimate_orientation_brute_force_2d(
                    epi_u[..., ch].astype(np.float64), **kwargs)

                disparity_u[s, :, ch], confidence_u[s, :, ch] = res

        # Estimate disparity for epi slices along v-direction
        disparity_v = np.zeros((s_max, t_max, num_ch))
        confidence_v = np.zeros(disparity_v.shape)
        for epi_v, t in self.epi_generator(method=epi_method, axis=0,
                                           coordinate=v_center):
            # Swap axis so EPI is of shape (v, t)
            epi_v = np.swapaxes(epi_v, 0, 1)

            # Iterate through color channels and estimate disparity
            for ch in range(0, self._numChannels):
                res = self._estimate_orientation_brute_force_2d(
                    epi_v[..., ch].astype(np.float64), **kwargs)
                disparity_v[:, t, ch], confidence_v[:, t, ch] = res

        # Set reliability of invalid pixels to minimum
        confidence_u[np.isnan(disparity_u) | np.isnan(confidence_u)] = 0
        confidence_v[np.isnan(disparity_v) | np.isnan(confidence_v)] = 0
        logger.info("...done")

        return disparity_u, disparity_v, confidence_u, confidence_v

    def _get_disparity_brute_force_4d(
            self,
            vmin: float, vmax: float,
            num_slopes: int = 40) -> Tuple[ndarray, ndarray]:
        """Calculates orientation of LF using 4D brute force fit.

        Args:


        Returns:
            Tuple of numpy arrays containing

                - **disparity**: A numpy array of shape (s, 1) or (t, 1),
                  representing disparity.
                - **confidence**: A numpy array of shape (s, 1) or (t, 1),
                  representing confidence in the disparity estimation.
                  Higher means better.

        """

        sigma = 0.5
        slopes = np.linspace(vmin, vmax, num_slopes)
        u_max, v_max, s_max, t_max, ch = self.shape

        variance = np.zeros((num_slopes, s_max, t_max, ch))

        for i in range(num_slopes):
            logger.info(f"Processing slope {i} of {num_slopes}...")
            u_slope = np.linspace(-0.5, 0.5, u_max) * slopes[i] * u_max
            v_slope = np.linspace(-0.5, 0.5, v_max) * slopes[i] * v_max
            lf_sheared = np.zeros(self.shape)

            for u in range(u_max):
                for v in range(v_max):
                    t_trans = skimage.transform.AffineTransform(
                        translation=(v_slope[v], u_slope[u]))

                    im_sheared = skimage.transform.warp(
                        np.squeeze(self[u, v]), t_trans, order=1)

                    lf_sheared[u, v] = gaussian_filter(im_sheared, sigma)

            lf_sheared = np.reshape(lf_sheared, (u_max*v_max, s_max, t_max, ch))

            variance[i, ...] = np.squeeze(np.var(lf_sheared, axis=0))

        # Get slope where variance is minimal
        disparity = -slopes[variance.argmin(axis=0)]

        # Calculate confidence
        #confidence = np.zeros(self.shape)
        grad_s = np.gradient(self, axis=2)
        grad_t = np.gradient(self, axis=3)
        confidence_full = np.hypot(grad_s, grad_t)
        u_c, v_c = np.ceil([0.5*u_max, 0.5*v_max]).astype(np.int)
        confidence = np.asarray(confidence_full[u_c, v_c])

        return disparity, confidence

    def get_disparity(self,
                      method: str = 'structure_tensor',
                      fusion_method: str = 'tv_l1',
                      vmin: float = -3, vmax: float = 3,
                      **kwargs) -> Tuple[ndarray, ndarray]:
        """Calculates a depth map from the light field.

        The depth is calculated from the 4D representation
        L(u,v,s,t) using orientation estimation on the epipolar
        plane images.

        Args:
            method: Method used for calculating the disparity. Possible values are:

                        * 'structure_tensor': Use the 2D structure tensor on EPI slice to calculate disparity
                        * 'brute_force_2d': Use brute force for 2D line fitting in EPI.

            fusion_method: Method for fusion of disparity maps from different LF axes.
                           Possible values are:

                               * 'average': Using average.
                               * 'weighted_average': Using weighted average.
                               * 'max_confidence': Using pixel wise maximum confidence.
                               * 'tv_l1': Total variation using L1 norm

            vmin: Minimum values that disparity is clipped with.
            vmax: Maximum values that disparity is clipped with.

        Returns:
            Tuple of numpy arrays containing

                * ``disparity``:
                    A numpy array of shape (s, t), representing disparity.
                * ``confidence``:
                    A numpy array of shape (s, t), representing confidence in
                    the disparity estimation. Higher is better.

        See Also:
            The disparity is estimated using :func:_estimate_orientation().

        """

        methods=['structure_tensor', 'brute_force_2d', 'brute_force_4d']
        fusion_methods = ['average', 'weighted_average', 'max_confidence', 'tv_l1']

        # Check arguments
        if method not in methods:
            raise NotImplementedError(f"Method '{method}' does not exist (yet?)")

        if fusion_method not in fusion_methods:
            raise NotImplementedError(f"Fusion method '{fusion_method}' does not exist.")

        logger.info(f"Calculating disparity using method '{method}'...")
        u_max, v_max, s_max, t_max, num_ch = self.shape

        if method == "structure_tensor":

            # Set default values for subroutines
            if not 'epi_method' in kwargs:
                kwargs = dict(epi_method='2D', **kwargs)

            res = self._get_disparity_structure_tensor(**kwargs)
            disp_u, disp_v, conf_u, conf_v = res
            conf_all = np.concatenate((conf_u, conf_v), axis=2)
            disp_all = np.concatenate((disp_u, disp_v), axis=2)

        elif method == "brute_force_2d":
            kwargs = {**kwargs, **dict(vmin=vmin, vmax=vmax)}
            res = self._get_disparity_brute_force_2d(**kwargs)
            disp_u, disp_v, conf_u, conf_v = res
            conf_all = np.concatenate((conf_u, conf_v), axis=2)
            disp_all = np.concatenate((disp_u, disp_v), axis=2)

        elif method == "brute_force_4d":
            kwargs = {**kwargs, **dict(vmin=vmin, vmax=vmax)}
            res = self._get_disparity_brute_force_4d(**kwargs)
            disp_all, conf_all = res

        logger.info(f"Fusing disparities using method '{fusion_method}'...")
        if fusion_method == 'average':

            # Weighted sum of disparities
            disparity = np.nanmean(disp_all, axis=-1)
            confidence = np.nanmean(conf_all, axis=-1)

        elif fusion_method == 'weighted_average':
            # Average weighted by confidence

            # Weighted sum of disparities
            confidence = np.nanmean(conf_all**2, axis=-1)
            disparity = np.nanmean(disp_all*conf_all**2, axis=-1)/confidence
            confidence = np.sqrt(confidence)

        elif fusion_method == 'max_confidence':
            # Select disparities with best confidence
            disparity = np.zeros((s_max, t_max))
            confidence = np.zeros(disparity.shape)
            maxima = np.amax(conf_all, axis=2, keepdims=True)
            mask = np.equal(conf_all, maxima)
            disparity = disp_all[mask].reshape(disparity.shape)
            confidence = conf_all[mask].reshape(confidence.shape)

        elif fusion_method == 'tv_l1':
            # Create stack of weights and normalize
            confidence_norm = (conf_all - conf_all.min()) / (conf_all.max() - conf_all.min())
            disparity = denoise.denoise_multi_images_tvl1(
                disp_all,
                n_iter=100,
                w_lambdas=confidence_norm)
            # Reset confidence, has no meaning anymore
            confidence = None

        logger.info("...done")

        return np.clip(disparity, vmin, vmax), confidence

    def get_refocus(self,
                    slopes: Union[float, List[float], ndarray],
                    aperture: Optional[Union[str, ndarray]] = None,
                    pre_interpolation: Optional[ndarray] = None) -> ndarray:
        """Get refocused image from the light field.

        The function calculates a 2D digitally refocused image from the 4D
        light field L(u,v,s,t) using a shifted summation over the light field.

        Args:
            slopes: The values by which the sub aperture views are shifted.
                This represents the depth at which the refocused image
                will be focused. A slope of 0 lies near the center of the
                light field's depth of field.

            aperture: Select a type of virtual aperture that is used for
                refocusing. It can either be specified by an aperture type
                name, see :func:`plenpy.utilities.kernels.get_avail_names()`
                for a list of available aperture names, or directly as a
                numpy array of shape (u_max, v_max). If ``None``, no aperture
                is used in the calculation.

            pre_interpolation: A numpy array of shape (u, v, numChannels).
                Each element in the array is a pre calculated
                interpolation object of type interp2d.

        Returns:
            The 2D refocused image as a numpy array of shape
            (s, t, num_channels), or a numpy array of shape
            (s, t, num_channels, num_slopes), when multiple input slopes are
            provided.
        """
        logger.info(f"Calculating light field refocus for slope: {slopes}...")

        # Get shape
        u_max, v_max, s_max, t_max, _ = self.shape

        # Set defaults
        if aperture is None:
            aperture = np.ones((u_max, v_max), dtype=np.float64)

        elif isinstance(aperture, str):
            aperture = kernels.get_kernel(aperture,
                                          size=u_max,
                                          size_y=v_max)

        else:
            aperture = aperture

        # Normalize
        aperture /= aperture.sum()

        # Convert slopes input to numpy array
        if issubclass(type(slopes), float) or issubclass(type(slopes), int):
            slopes = np.asarray([slopes])
        else:
            slopes = np.asarray(slopes)

        # Get offset with defined slope (Different slopes in u, v possible)
        # Offset symmetric around zero: -u/2 to u/2
        v_slope = np.linspace(-0.5, 0.5, v_max) * v_max
        u_slope = np.linspace(-0.5, 0.5, u_max) * u_max

        # Shift light field with desired slope
        img_refocused = np.zeros((s_max,
                                  t_max,
                                  self._numChannels,
                                  slopes.size))

        # Grid to use in interpolation
        t = np.arange(0, t_max)
        s = np.arange(0, s_max)

        for v in range(0, v_max):
            for u in range(0, u_max):
                # Refocus separately for every color channel
                for chn in range(0, self._numChannels):
                    # Get slice in u-v-plane and interpolate missing values
                    # to get the shifted slice
                    # L_interp(v,u,t,s) = L(v,u,v*v_slope+t,u*u_slope+s)
                    if pre_interpolation is None:
                        tmp = interpolate.interp2d(
                            s,
                            t,
                            np.swapaxes(self[u, v, :, :, chn], 0, 1),
                            kind='linear')
                    else:
                        # Pre calculated interpolation functions
                        tmp = pre_interpolation[v, u, chn]

                    # Every slope can use the same interpolation function
                    for slp in range(0, slopes.size):
                        # Sum over shifted light field to get refocused image
                        img_refocused[:, :, chn, slp] += \
                            (aperture[u, v]*tmp(s + u_slope[u]*slopes[slp],
                                                t + v_slope[v]*slopes[slp])).T
            # Show progress
            sys.stdout.write('\r')
            sys.stdout.write(
                "[%-20s] %d%%" % ('=' * int(20 * (v+1) / v_max),
                                  100*(v+1)/v_max))
            sys.stdout.flush()
        sys.stdout.write('\n')

        # Normalize
        img_refocused = skimage.img_as_float(img_refocused)
        logger.info("...done")
        return np.swapaxes(np.squeeze(img_refocused), 0, 1)

    def get_all_in_focus(
            self,
            slope_map: Optional[ndarray] = None,
            aperture_type: Optional[str] = None,
            virtual_aperture: Optional[ndarray] = None) -> ndarray:
        """Get completely focused image from the light field.

        The focus plane for each pixel is calculated in a way, that every pixel
        is in focus.

        Args:
            slope_map: The values by which the sub aperture views are shifted.
                If no map is specified, it will be calculated.

            aperture_type: Select type of the virtual aperture that is
                used for refocusing. Possible values are according to
                :func:`plenpy.utilities.kernels.get_kernel` name option.

            virtual_aperture : The 2D virtual aperture, represented as
                a numpy array of shape (u, v).

        Returns:
            The 2D all refocused image, represented by a numpy array of shape
            (s, t, num_channels).
        """
        # Get shape
        u_max, v_max, s_max, t_max, _ = self.shape

        # Define virtual aperture and normalize
        if aperture_type is not None:
            aperture = kernels.get_kernel(aperture_type,
                                          size=u_max,
                                          size_y=v_max)
        elif virtual_aperture is not None:
            aperture = virtual_aperture
        else:
            aperture = np.ones((u_max, v_max), dtype=np.float64)
        aperture /= aperture.sum()

        if slope_map is None:
            slope_map, confidence = self.get_depth()
            threshold = 0.9
            slope_map = images.remove_outliers(slope_map,
                                               confidence,
                                               threshold)
            slope_map[np.isnan(slope_map)] = 0

        # Get offset with defined slope (Different slopes in u, v possible)
        # Offset symmetric around zero: -u/2 to u/2
        v_slope = np.linspace(-0.5, 0.5, v_max) * v_max
        u_slope = np.linspace(-0.5, 0.5, u_max) * u_max

        # Shift light field with desired slope
        img_out = np.zeros((s_max,
                            t_max,
                            self._numChannels))

        # Grid to use in interpolation
        t = np.arange(0, t_max)
        s = np.arange(0, s_max)
        ss, tt = np.meshgrid(s, t)
        points = (ss.ravel(), tt.ravel())
        slope_map = slope_map.transpose().ravel()

        for v in range(0, v_max):
            for u in range(0, u_max):
                # Refocus separately for every color channel
                for chn in range(0, self._numChannels):
                    # Get slice in u-v-plane and interpolate missing values to
                    # get the shifted slice
                    # L_interp(v,u,t,s) = L(v,u,v*v_slope+t,u*u_slope+s)

                    tmp = RGI((s, t),
                              self[u, v, :, :, chn],
                              method='linear',
                              bounds_error=False,
                              fill_value=0)
                    # Sum over shifted light field to get refocused image
                    img_out[:, :, chn] += \
                        aperture[u, v]*tmp((points[0] + u_slope[u] * slope_map,
                                            points[1] + v_slope[v] * slope_map)
                                           ).reshape((s_max, t_max))

            # Show progress
            sys.stdout.write('\r')
            sys.stdout.write(
                "[%-20s] %d%%" % ('=' * int(20 * (v + 1) / v_max),
                                  100*(v + 1)/v_max))
            sys.stdout.flush()
        sys.stdout.write('\n')

        # Normalize
        img_out = skimage.img_as_float(img_out)

        return np.swapaxes(np.squeeze(img_out), 0, 1)

    @staticmethod
    def filter_depth_map(depth: ndarray,
                         confidence: Optional[ndarray] = None,
                         method: Optional[str] = None) -> ndarray:
        """Filter a depth map.

        The map is filtered using the provided confidence.

        Args:
            depth: The depth map of shape (s_max, t_max)

            confidence: The confidence of the depth estimation.
                Has to be of same shape as ``depth``.

            method: Method used to filter the depth map. Possible values are:\n
                * 'blur'
                * 'outliers'
                * 'TV-L1'
                * 'ROF'

        Returns:
            The filtered depth map, a numpy array of shape (s_max, t_max).
        """

        param_list = ['blur', 'outliers', 'TV-L1', 'ROF']

        if method is None:
            method = 'blur'

        if method not in param_list:
            raise ValueError(
                "Specified image gradient type is not one of the recognized "
                f"methods: {param_list}")

        elif method == 'blur':
            sigma = 2.0  # TODO: define as input to method
            return gaussian_filter(depth, sigma)

        elif method == 'outliers':
            if confidence is None:
                raise ValueError(
                    "Please provide confidence map for outlier removal.")
            threshold = 0.9  # TODO: define as input to method
            return images.remove_outliers(depth, confidence, threshold)

        elif method == 'TV-L1':
            if confidence is None:
                confidence = 1
            return images.denoise_image_tvl1(depth,
                                             n_iter=100,
                                             w_lambda=1.0*confidence)
        elif method == 'ROF':
            if confidence is None:
                confidence = 1
            return images.denoise_image_rof(depth,
                                            n_iter=100,
                                            w_lambda=1.0*confidence)
        else:
            raise NotImplementedError(f"'{method}' has not been implemented yet.")


    @staticmethod
    def _get_valid_dtype(data: ndarray) -> Type[Union[np.float64, np.uint16]]:
        """Extract a valid dtype from an array.

        If the data is of type ``float``, ``numpy.float64`` is returned,
        if of type ``uint`` or ``int``, type ``np.uint16`` is returned.
        Otherwise a ``ValueError`` is raised.

        This is useful, since LightField only accepts float64 or uint16.
        """

        if data.dtype in [np.float, np.float16, np.float32, np.float64]:
            dtype = np.float64

        elif data.dtype in [np.int, np.int8, np.int16, np.uint8, np.uint16]:
            dtype = np.uint16

        else:
            raise ValueError("The data has invalid dtype '{img.dtype}'."
                             " Please convert to a valid dtype first.")

        return dtype

    def show_depth(self, hsv: bool = True, plt_show: bool = True):
        """ Show the depth map of the light field.

         The depth map is calculated using :func:`get_depth()`.
         The map is filtered using :func:`filter_depth_map()` using
         the 'outliers' method.

         Args:
            hsv: Flag indicating whether to show the map and its confidence
                using the HSV color space. The depth will be coded by color,
                the confidence codes the saturation. I.e. pixels with low
                confidence will appear grey, with high confidence in color.

            plt_show: Flag indicating whether to call
                :func:`.matplotlib.pyplot.show()` before returning or not.
                Default value is ``True``.

        """
        disp, conf = self.get_depth()

        #disp = LightField.filter_depth_map(disp, conf, method='outliers')

        if hsv:
            hue = disp
            sat = conf
            val = np.ones(disp.shape)

            hsv = np.stack((hue, sat, val), axis=2)
            print(hue.shape)
            print(hsv.shape)

            img = matplotlib.colors.hsv_to_rgb(hsv)

        else:
            img = disp

        plt.imshow(np.squeeze(img))

        if plt_show is True:
            plt.show()

        return

    def show_subaperture(self,
                         u: int,
                         v: int):
        """Show a subaperture view of the light field.

        Args:
            u: Fixed u-coordinate of the subaperture view.

            v: Fixed v-coordinate of the subaperture view.

        """

        im = self.get_subaperture(u, v, copy=False)
        # Normalize before imshow
        im = skimage.img_as_float(im)
        plt.imshow(np.squeeze(im))
        plt.show()
        return

    def show_subaperture_sequence(self):
        """Plot an animated sequence of subaperture views.

        The plot shows subapertures of the light field lying on a circle
        around the central subaperture view.
        """

        title = 'Sequence of sub aperture views'
        plt.figure(title)

        phi = 0
        img = None
        while plt.fignum_exists(title):
            # Convert degrees to radian, divide by 2pi
            phi_rad = phi*0.15915494309189535
            phi = (phi + 1) % 360

            # Calculate u,v via polar coordinates to get a circular
            # moving sequence of subaperture views.
            r = int(self.shape[0] / 2.0)
            u = int(int(self.shape[0] / 2.0) + r * np.sin(phi_rad))
            v = int(int(self.shape[1] / 2.0) + r * np.cos(phi_rad))

            im = self.get_subaperture(u, v, copy=False)

            # Normalize before imshow
            im = skimage.img_as_float(im)

            if img is None:
                img = plt.imshow(np.squeeze(im))
            else:
                img.set_data(im)
            try:
                plt.pause(.025)
                plt.draw()
            except TclError:
                # Stop sequence and close window when plotting/pause fails
                plt.close(title)
                return
        return

    def show_focus_stack_sequence(self, focus_stack: Optional[ndarray] = None):
        """Plot an animated sequence of refocused images from the light field.

        Args:
            focus_stack: A numpy array representing the stack of refocused
                images (s, t, num_channels, num_images).
                If no stack is specified, the stack for slopes
                [-1, -0.5, 0, 0.5, 1] is calculated.

        """

        if focus_stack is None:
            focus_stack = self.get_refocus([-1, -0.5, 0, 0.5, 1])

        if focus_stack.ndim == 3:
            # Add singleton dimension
            focus_stack = focus_stack[..., np.newaxis]

        pause = 5.0/focus_stack.shape[-1]

        title = 'Sequence of refocused images'
        plt.figure(title)

        img = None
        i = 0
        while plt.fignum_exists(title):
            # Normalize before imshow
            im = skimage.img_as_float(focus_stack[..., i])
            if img is None:
                img = plt.imshow(np.squeeze(im))
            else:
                img.set_data(np.squeeze(im))
            try:
                plt.pause(pause)
                plt.draw()
            except TclError:
                # Stop sequence and close window when plotting/pause fails
                plt.close(title)
                return
            i = (i + 1) % focus_stack.shape[-1]
        return

    def show_refocus_interactive(self, depth: Optional[ndarray] = None):
        """Plot a refocused subaperture view of the light field.

        Clicking in the plot refocuses the image to the plane that the click
        happened on. Press ENTER to show all-in-focus image.

        Args:
            depth: A numpy array representing the depth/epi-slopes.
                This is used to calculate the refocus plane.
                If no depth map is specified, one will be calculated.

        """

        # Calculate depth if no depth is provided
        if depth is None:
            depth, confidence = self.get_depth()
            threshold = 0.9
            depth = images.remove_outliers(depth, confidence, threshold)
            depth[np.isnan(depth)] = 0

        # Calculate interpolation functions to speed up interactive refocusing
        interp_funcs = np.zeros((self.shape[1], self.shape[0], self._numChannels),
                                dtype=object)
        t = np.arange(0, self.shape[3])
        s = np.arange(0, self.shape[2])
        for v in range(0, self.shape[1]):
            for u in range(0, self.shape[0]):
                # Refocus separately for every color channel
                for chn in range(0, self._numChannels):
                    interp_funcs[v, u, chn] = interpolate.interp2d(
                        s,
                        t,
                        np.swapaxes(self[u, v, :, :, chn], 0, 1),
                        kind='linear')

        # Show center sub aperture view as initial image
        title = 'Refocused image. Click on image to change focus. '
        title += 'Press ENTER for all in focus image.'
        fig = plt.figure(title)
        im = self.get_subaperture(round((self.shape[0] - 1) / 2.0),
                                  round((self.shape[1] - 1) / 2.0),
                                  copy=False)

        # Normalize before imshow
        im = skimage.img_as_float(im)

        img = plt.imshow(np.squeeze(im))
        plt.pause(.025)
        plt.draw()

        # Coordinates for click
        click_coords = (0, 0)

        # Function to get click event
        def onclick(event):
            nonlocal click_coords, depth, img, im, self, interp_funcs
            try:
                click_coords = (int(event.ydata), int(event.xdata))
            except TypeError:
                print('Please click inside the image.')
                return

            # Extract slope value for specified coordinates
            slope = depth[click_coords[0], click_coords[1]]
            print('Refocus to {:0.4f}'.format(slope))

            # Refocus image with extracted slope value
            im = self.get_refocus(slope, pre_interpolation=interp_funcs)

            # Normalization
            im = skimage.img_as_float(im)
            img.set_data(np.squeeze(im))
            plt.draw()
            return

        def onkey(event):
            nonlocal depth, img, im, self
            if event.key == 'enter':
                print('All in focus image')
                im = self.get_all_in_focus(depth)
                img.set_data(im)
                plt.draw()
                return

        # Wait for click or keyboard input get new image
        fig.canvas.mpl_connect('button_press_event', onclick)
        fig.canvas.mpl_connect('key_press_event', onkey)
        plt.show()
        return

    def show(self, plt_show: bool = True):
        """ Show the 4D light field.

         Shown is a 2D representation of the light field,
         corresponding to the collection of subaperture views,
         using matplotlib.
         The conversion is calculated using :func:`._four_d_to_two_d()`

         Args:
            plt_show: Flag indicating whether to call
                :func:`.matplotlib.pyplot.show()` before returning or not.
                Default value is ``True``.

        """
        data = LightField._4d_to_2d(self)

        if data.dtype == np.uint16:
            data = (data/255.0).astype(np.uint8)

        plt.imshow(np.squeeze(data))

        if plt_show is True:
            plt.show()
        return

    def show_interactive(self, rev_color_ch: Optional[bool] = None):
        """Visualize the light field interactively.

         This is done by plotting sub aperture views using matplotlib and
         panning through the views using the mouse. Click on the image
         and drag the mouse to move to a different sub aperture view.
         Right click resets to center view.

         Use scrolling to scroll through the color channels. This is
         particularly useful for hyperspectral light field data.
         Enable per-color-channel view by clicking the scroll wheel once.
         Reset to the regular view by double clicking the scroll wheel.

         Double click onto the subaperture opens a new figure showing the
         spectrum of the corresponding pixel.

         Args:
            rev_color_ch: Reverse the order of the color channels in the
                scrolling color channel view. By default, the channels are
                shown from small (~400 nm) to large (~700nm) wavelenghts as
                this is the standard ordering of color channels. If the
                channels are ordered from large to small, set to ``True``.
                This is automatically done for three channel RGB images.
                If e.g.  a three channel image is in BGR format,
                set to ``False``.

        """
        u, v, s, t, num_ch = self.shape

        # Flag whether scrolling is possible
        is_scrollable = True if num_ch > 1 else False

        # Flag whether to reverse color channels, e.g. for RGB images
        if rev_color_ch is None:
            rev_color_ch = True if num_ch == 3 else False

        # Flag whether scrolling was enabled
        scroll_enabled = False

        # Variables to drag image and check mouse click
        press = None
        u_current = max(round((u - 1) / 2.0), 0)
        v_current = max(round((v - 1) / 2.0), 0)

        # Wavelengths for color images to scroll through
        lambda_start = 430
        lambda_end = 650
        wavelength_list = np.linspace(lambda_start, lambda_end, num_ch)

        if rev_color_ch:
            wavelength_list = np.flipud(wavelength_list)

        # Index of the current wavelength, start at lambda_start
        curr_wave_index = 0

        # Get color converter instance, calculate RGB values of wavelengths
        converter = colors.WavelengthConverter()
        wavelength_rgb = converter.to_rgb(wavelength_list)

        # Initially show center sub aperture view
        im = self[u_current, v_current, :, :, :]
        if num_ch > 3:
            logger.info("Converting spectra to RGB image...")
            sp_converter = colors.SpectrumConverter(wavelength_list)

            # Create rgb lf data from hs data
            rgb_data = np.zeros((u, v, s, t, 3))

            # Reshape to get one spectrum per column
            spectra = np.reshape(self, (u*v*s*t, num_ch))

            rgb = sp_converter.to_rgb(spectra)

            rgb_data = np.reshape(rgb, rgb_data.shape)
            logger.info("...done.")
            im = rgb_data[u_current, v_current, :, :, :]

        fig = plt.figure('Click and drag to view light field. '
                         'Press scroll wheel for color channel view.')
        img = plt.imshow(np.squeeze(im), cmap='gray')
        plt.title(f"Subaperture for (u, v) = "
                  f"{int(u_current), int(v_current)}")
        plt.xlabel("t")
        plt.ylabel("s")

        plt.pause(.025)
        plt.draw()

        def draw_canvas(color_index=None):
            nonlocal im, img, u_current, v_current, is_scrollable

            if num_ch == 1 or num_ch == 3:
                im = self[int(u_current), int(v_current), :, :, :]

            if num_ch > 3:
                im = rgb_data[int(u_current), int(v_current), :, :, :]

            if color_index is not None and scroll_enabled:

                rgb = wavelength_rgb[color_index]

                # Select sub view, mono channel
                im = self[int(u_current), int(v_current), :, :, color_index]

                # Calculate mono color representation
                im = np.reshape(np.outer(im, rgb), im.shape + (3,))

            # Set new image
            plt.title(f"Subaperture for (u, v) = "
                      f"{int(u_current), int(v_current)}")
            img.set_data(np.squeeze(im))
            fig.canvas.draw()

            return

        def draw_spectrum(u: int, v: int, s: int, t:int):
            if s is None or t is None:
                logger.info("You have clicked outside of the image...")
                return

            u, v, s, t = int(u), int(v), int(s), int(t)
            logger.info(f"Plotting spectrum of (u, v, s, t) = "
                        f"{u, v, s, t}.")

            x_data = np.arange(0, num_ch)
            y_data = self[u, v, s, t, :]
            plt.figure("Spectrum")
            plt.title(f"Spectrum of (u, v, s, t) = {u, v, s, t}.")
            plt.scatter(x_data, y_data)
            plt.xlabel("Color channel")
            plt.ylabel("Reflectance")
            plt.ylim(0, 1)

            # Set the color channel labels to integer
            ch_int = range(0, num_ch)
            if len(ch_int) > 10:
                ch_int = ch_int[::2]

            plt.xticks(ch_int)
            plt.show()

            return

        def on_press(event):
            nonlocal press, im, img, u_current, v_current, scroll_enabled

            # On Double click on button 1: show spectrum
            if event.dblclick and event.button == 1:
                s, t = event.ydata, event.xdata

                draw_spectrum(u_current, v_current, s=s, t=t)

                return

            # On Right click: Reset to center view.
            if event.button == 3:
                logger.info("Resetting to center view.")
                press = None
                u_current = max(round((u - 1) / 2.0), 0)
                v_current = max(round((v - 1) / 2.0), 0)

                draw_canvas(curr_wave_index)
                return

            # On double click of scroll wheel: Set scroll modus
            if event.button == 2:
                if not is_scrollable:
                    logger.info("Scrolling is not possible for b&w images.")
                elif scroll_enabled:
                    # Reset on double scroll wheel click
                    logger.info("Resetting to normal modus.")
                    scroll_enabled = False
                    draw_canvas()
                    return

                elif is_scrollable and not scroll_enabled:
                    logger.info("Setting scroll modus.")
                    logger.info(f"Showing color channel {curr_wave_index}.")

                    scroll_enabled = True
                    draw_canvas(curr_wave_index)

                    return

            # On button press get coordinates
            press = event.xdata, event.ydata

        def on_motion(event):
            nonlocal press, self, u_current, v_current, img, im
            nonlocal curr_wave_index
            # On motion we will move through the light field
            if press is None:
                return
            if event.inaxes is None:
                return
            if (press[0] is None) or (press[1] is None):
                return

            dx = event.xdata - press[0]
            dy = event.ydata - press[1]
            press = (event.xdata, event.ydata)

            # Reduce rate
            rate = 30

            u_current = max(0, min(u - 1, u_current - dy / rate))
            v_current = max(0, min(v - 1, v_current - dx / rate))

            draw_canvas(curr_wave_index)

        def on_scroll(event):
            # When scrolling, show color channels seperately
            nonlocal scroll_enabled, curr_wave_index

            if event.button == 'up' and scroll_enabled:
                # Scroll up increases color channel
                curr_wave_index += 1
                curr_wave_index = min(num_ch - 1, curr_wave_index)

                logger.info(f"Showing color channel {curr_wave_index}.")

                draw_canvas(curr_wave_index)
                return

            if event.button == 'down' and scroll_enabled:
                # Scroll down decreases color channel
                curr_wave_index -= 1
                curr_wave_index = max(0, curr_wave_index)

                logger.info(f"Showing color channel {curr_wave_index}.")

                draw_canvas(curr_wave_index)
                return

        def on_release(event):
            nonlocal press
            # On release we reset the press data
            press = None
            fig.canvas.draw()

        # Connect to matplotlib event API
        fig.canvas.mpl_connect('button_press_event', on_press)
        fig.canvas.mpl_connect('button_release_event', on_release)
        fig.canvas.mpl_connect('motion_notify_event', on_motion)
        fig.canvas.mpl_connect('scroll_event', on_scroll)
        plt.show()
        return

