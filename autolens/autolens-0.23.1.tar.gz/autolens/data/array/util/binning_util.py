from autolens import decorator_util
import numpy as np

from autolens.data.array.util import array_util, mask_util


@decorator_util.jit()
def padded_binning_shape_2d_from_shape_2d_and_bin_up_factor(shape_2d, bin_up_factor):

    shape_remainder = (shape_2d[0] % bin_up_factor, shape_2d[1] % bin_up_factor)

    if shape_remainder[0] != 0 and shape_remainder[1] != 0:
        shape_pad = (bin_up_factor - shape_remainder[0], bin_up_factor - shape_remainder[1])
    elif shape_remainder[0] != 0 and shape_remainder[1] == 0:
        shape_pad = (bin_up_factor - shape_remainder[0], 0)
    elif shape_remainder[0] == 0 and shape_remainder[1] != 0:
        shape_pad = (0, bin_up_factor - shape_remainder[1])
    else:
        shape_pad = (0, 0)

    return (shape_2d[0] + shape_pad[0], shape_2d[1] + shape_pad[1])

@decorator_util.jit()
def padded_binning_array_2d_from_array_2d_and_bin_up_factor(array_2d, bin_up_factor, pad_value=0.0):
    """If an array is to be binned up, but the dimensions are not divisible by the bin-up factor, this routine pads \
    the array to make it divisible.

    For example, if the array is shape (5,5) and the bin_up_factor is 2, this routine will pad the array to shape \
    (6,6).

    Parameters
    ----------
    array_2d : ndarray
        The 2D array that is padded.
    bin_up_factor : int
        The factor which the array is binned up by (e.g. a value of 2 bins every 2 x 2 pixels into one pixel).
    pad_value : float
        If the array is padded, the value the padded edge values are filled in using.

    Returns
    -------
    ndarray
        The 2D array that is padded before binning up.

    Examples
    --------
    array_2d = np.ones((5,5))
    padded_array_2d = padded_array_2d_for_binning_up_with_bin_up_factor( \
        array_2d=array_2d, bin_up_factor=2, pad_value=0.0)
    """

    padded_binning_shape_2d = padded_binning_shape_2d_from_shape_2d_and_bin_up_factor(
        shape_2d=array_2d.shape, bin_up_factor=bin_up_factor)

    return array_util.resized_array_2d_from_array_2d_and_resized_shape(
        array_2d=array_2d, resized_shape=padded_binning_shape_2d, pad_value=pad_value)

@decorator_util.jit()
def binned_up_array_2d_using_mean_from_array_2d_and_bin_up_factor(array_2d, bin_up_factor):
    """Bin up an array to coarser resolution, by binning up groups of pixels and using their mean value to determine \
     the value of the new pixel.

    If an array of shape (8,8) is input and the bin up size is 2, this would return a new array of size (4,4) where \
    every pixel was the mean of each collection of 2x2 pixels on the (8,8) array.

    If binning up the array leads to an edge being cut (e.g. a (9,9) array binned up by 2), the array is first \
    padded to make the division work. One must be careful of edge effects in this case.

    Parameters
    ----------
    array_2d : ndarray
        The 2D array that is binned up.
    bin_up_factor : int
        The factor which the array is binned up by (e.g. a value of 2 bins every 2 x 2 pixels into one pixel).

    Returns
    -------
    ndarray
        The binned up 2D array from the input 2D array.

    Examples
    --------
    array_2d = np.ones((5,5))
    resize_array = bin_up_array_2d_using_mean(array_2d=array_2d, bin_up_factor=2)
    """

    padded_binning_array_2d = padded_binning_array_2d_from_array_2d_and_bin_up_factor(
        array_2d=array_2d, bin_up_factor=bin_up_factor)

    binned_array_2d = np.zeros(shape=(padded_binning_array_2d.shape[0] // bin_up_factor,
                                      padded_binning_array_2d.shape[1] // bin_up_factor))

    for y in range(binned_array_2d.shape[0]):
        for x in range(binned_array_2d.shape[1]):
            value = 0.0
            for y1 in range(bin_up_factor):
                for x1 in range(bin_up_factor):
                    padded_y = y*bin_up_factor + y1
                    padded_x = x*bin_up_factor + x1
                    value += padded_binning_array_2d[padded_y, padded_x]

            binned_array_2d[y,x] = value / (bin_up_factor ** 2.0)

    return binned_array_2d

@decorator_util.jit()
def binned_array_2d_using_quadrature_from_array_2d_and_bin_up_factor(array_2d, bin_up_factor):
    """Bin up an array to coarser resolution, by binning up groups of pixels and using their quadrature value to \
    determine the value of the new pixel.

    If an array of shape (8,8) is input and the bin up size is 2, this would return a new array of size (4,4) where \
    every pixel was the quadrature of each collection of 2x2 pixels on the (8,8) array.

    If binning up the array leads to an edge being cut (e.g. a (9,9) array binned up by 2), the array is first \
    padded to make the division work. One must be careful of edge effects in this case.

    Parameters
    ----------
    array_2d : ndarray
        The 2D array that is binned up.
    bin_up_factor : int
        The factor which the array is binned up by (e.g. a value of 2 bins every 2 x 2 pixels into one pixel).

    Returns
    -------
    ndarray
        The binned up 2D array from the input 2D array.

    Examples
    --------
    array_2d = np.ones((5,5))
    resize_array = bin_up_array_2d_using_quadrature(array_2d=array_2d, bin_up_factor=2)
    """

    padded_binning_array_2d = padded_binning_array_2d_from_array_2d_and_bin_up_factor(
        array_2d=array_2d, bin_up_factor=bin_up_factor)

    binned_array_2d = np.zeros(shape=(padded_binning_array_2d.shape[0] // bin_up_factor,
                                      padded_binning_array_2d.shape[1] // bin_up_factor))

    for y in range(binned_array_2d.shape[0]):
        for x in range(binned_array_2d.shape[1]):
            value = 0.0
            for y1 in range(bin_up_factor):
                for x1 in range(bin_up_factor):
                    padded_y = y*bin_up_factor + y1
                    padded_x = x*bin_up_factor + x1
                    value += padded_binning_array_2d[padded_y, padded_x] ** 2.0

            binned_array_2d[y,x] = np.sqrt(value) / (bin_up_factor ** 2.0)

    return binned_array_2d

@decorator_util.jit()
def binned_array_2d_using_sum_from_array_2d_and_bin_up_factor(array_2d, bin_up_factor):
    """Bin up an array to coarser resolution, by binning up groups of pixels and using their sum value to determine \
     the value of the new pixel.

    If an array of shape (8,8) is input and the bin up size is 2, this would return a new array of size (4,4) where \
    every pixel was the sum of each collection of 2x2 pixels on the (8,8) array.

    If binning up the array leads to an edge being cut (e.g. a (9,9) array binned up by 2), the array is first \
    padded to make the division work. One must be careful of edge effects in this case.

    Parameters
    ----------
    array_2d : ndarray
        The 2D array that is binned up.
    bin_up_factor : int
        The factor which the array is binned up by (e.g. a value of 2 bins every 2 x 2 pixels into one pixel).

    Returns
    -------
    ndarray
        The binned up 2D array from the input 2D array.

    Examples
    --------
    array_2d = np.ones((5,5))
    resize_array = bin_up_array_2d_using_sum(array_2d=array_2d, bin_up_factor=2)
    """

    padded_binning_array_2d = padded_binning_array_2d_from_array_2d_and_bin_up_factor(
        array_2d=array_2d, bin_up_factor=bin_up_factor)

    binned_array_2d = np.zeros(shape=(padded_binning_array_2d.shape[0] // bin_up_factor,
                                      padded_binning_array_2d.shape[1] // bin_up_factor))

    for y in range(binned_array_2d.shape[0]):
        for x in range(binned_array_2d.shape[1]):
            value = 0.0
            for y1 in range(bin_up_factor):
                for x1 in range(bin_up_factor):
                    padded_y = y*bin_up_factor + y1
                    padded_x = x*bin_up_factor + x1
                    value += padded_binning_array_2d[padded_y, padded_x]

            binned_array_2d[y,x] = value

    return binned_array_2d

@decorator_util.jit()
def binned_up_mask_2d_from_mask_2d_and_bin_up_factor(mask_2d, bin_up_factor):
    """Bin up an array to coarser resolution, by binning up groups of pixels and using their sum value to determine \
     the value of the new pixel.

    If an array of shape (8,8) is input and the bin up size is 2, this would return a new array of size (4,4) where \
    every pixel was the sum of each collection of 2x2 pixels on the (8,8) array.

    If binning up the array leads to an edge being cut (e.g. a (9,9) array binned up by 2), an array is first \
    extracted around the centre of that array.


    Parameters
    ----------
    mask_2d : ndarray
        The 2D array that is resized.
    new_shape : (int, int)
        The (y,x) new pixel dimension of the trimmed array.
    origin : (int, int)
        The oigin of the resized array, e.g. the central pixel around which the array is extracted.

    Returns
    -------
    ndarray
        The resized 2D array from the input 2D array.

    Examples
    --------
    array_2d = np.ones((5,5))
    resize_array = resize_array_2d(array_2d=array_2d, new_shape=(2,2), origin=(2, 2))
    """

    padded_mask_2d = padded_binning_array_2d_from_array_2d_and_bin_up_factor(
        array_2d=mask_2d, bin_up_factor=bin_up_factor, pad_value=True)

    binned_mask_2d = np.zeros(shape=(padded_mask_2d.shape[0] // bin_up_factor,
                                      padded_mask_2d.shape[1] // bin_up_factor))

    for y in range(binned_mask_2d.shape[0]):
        for x in range(binned_mask_2d.shape[1]):
            value = True
            for y1 in range(bin_up_factor):
                for x1 in range(bin_up_factor):
                    padded_y = y*bin_up_factor + y1
                    padded_x = x*bin_up_factor + x1
                    if padded_mask_2d[padded_y, padded_x] == False:
                        value = False

            binned_mask_2d[y,x] = value

    return binned_mask_2d

@decorator_util.jit()
def binned_mask_2d_mapper_from_mask_2d_and_bin_up_factor(mask_2d, bin_up_factor):
    """Create a 2D mask which effectively maps a 2D mask to a 2D binned mask. wE create a mask the same shape \
    as the 2D mask, but in each binned up region set all values equal to True except for one value (the central \
    value).
    
    This provides us with a mask which we can iterate over to count the indexes of binned up pixels, whilst using \ 
    the original 2D mask to keep track of the mask's indexes. This is used for mapping binned up masked array index's \
    to the original mask's indexes.
    
    For example, if we had a 6x6 mask of all False:
    
    [[False, False, False, False, False, False],
     [False, False, False, False, False, False],
     [False, False, False, False, False, False],
     [False, False, False, False, False, False],
     [False, False, False, False, False, False],
     [False, False, False, False, False, False]]
     
    For a bin_up_factor of 3, the resulting padded mask mapper is as follows:
    
    [[True, True, True, True, True, True],
     [True, False, True, True, False, True],
     [True, True, True, True, True, True],
     [True, True, True, True, True, True],
     [True, False, True, True, False, True],
     [True, True, True, True, True, True]]

    The above mask then masks it much easier to pair masked binned up indexes to the original mask's indexes.

    Parameters
    ----------
    mask_2d : ndarray
        The 2D mask that the
    bin_up_factor : int
        The factor which the array is binned up by (e.g. a value of 2 bins every 2 x 2 pixels into one pixel).

    Returns
    -------
    ndarray
        The binned up 2D array from the input 2D array.

    Examples
    --------
    mask_2d = np.full(fill_value=False, shape=(9,9))
    binned_mask_2d_mapper = binned_mask_2d_mapper_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=3)
    """

    padded_mask_2d = padded_binning_array_2d_from_array_2d_and_bin_up_factor(
        array_2d=mask_2d, bin_up_factor=bin_up_factor, pad_value=True)

    binned_mask_2d = binned_up_mask_2d_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=bin_up_factor)

    binned_mask_2d_mapper = np.full(fill_value=True, shape=padded_mask_2d.shape)

    for bin_y in range(binned_mask_2d.shape[0]):
        for bin_x in range(binned_mask_2d.shape[1]):
            if binned_mask_2d[bin_y, bin_x] == False:
                mask_entry_found = False
                for bin_y1 in range(bin_up_factor):
                    for bin_x1 in range(bin_up_factor):
                        mask_y = bin_y*bin_up_factor + bin_y1
                        mask_x = bin_x*bin_up_factor + bin_x1
                        if padded_mask_2d[mask_y, mask_x] == False and not mask_entry_found:
                            binned_mask_2d_mapper[mask_y, mask_x] = False
                            mask_entry_found = True

    return binned_mask_2d_mapper

@decorator_util.jit()
def binned_masked_array_1d_to_masked_array_1d_from_mask_2d_and_bin_up_factor(mask_2d, bin_up_factor):

    padded_mask_2d = padded_binning_array_2d_from_array_2d_and_bin_up_factor(
        array_2d=mask_2d, bin_up_factor=bin_up_factor, pad_value=True)

    binned_mask_2d_mapper = binned_mask_2d_mapper_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=bin_up_factor)

    total_binned_masked_pixels = mask_util.total_regular_pixels_from_mask(mask=binned_mask_2d_mapper)

    binned_masked_array_1d_to_masked_array_1d = np.zeros(total_binned_masked_pixels)

    binned_mask_index = 0
    mask_index = 0

    for mask_y in range(padded_mask_2d.shape[0]):
        for mask_x in range(padded_mask_2d.shape[1]):
            if binned_mask_2d_mapper[mask_y, mask_x] == False:
                binned_masked_array_1d_to_masked_array_1d[binned_mask_index] = mask_index
                binned_mask_index += 1
            if padded_mask_2d[mask_y, mask_x] == False:
                mask_index += 1

    return binned_masked_array_1d_to_masked_array_1d

@decorator_util.jit()
def masked_array_1d_to_binned_masked_array_1d_from_mask_2d_and_bin_up_factor(mask_2d, bin_up_factor):

    padded_mask_2d = padded_binning_array_2d_from_array_2d_and_bin_up_factor(
        array_2d=mask_2d, bin_up_factor=bin_up_factor, pad_value=True)

    binned_mask_2d = binned_up_mask_2d_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=bin_up_factor)

    binned_mask_2d_mapper = binned_mask_2d_mapper_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=bin_up_factor)

    total_masked_pixels = mask_util.total_regular_pixels_from_mask(mask=padded_mask_2d)

    masked_array_1d_to_binned_masked_array_1d = np.zeros(total_masked_pixels)

    binned_mask_index = 0
    mask_index = 0

    for bin_y in range(binned_mask_2d.shape[0]):
        for bin_x in range(binned_mask_2d.shape[1]):
            if binned_mask_2d[bin_y, bin_x] == False:
                for bin_y1 in range(bin_up_factor):
                    for bin_x1 in range(bin_up_factor):
                        mask_y = bin_y*bin_up_factor + bin_y1
                        mask_x = bin_x*bin_up_factor + bin_x1
                        if padded_mask_2d[mask_y, mask_x] == False and not mask_entry_found:
                            binned_mask_2d_mapper[mask_y, mask_x] = False
                            mask_entry_found = True

    for mask_y in range(padded_mask_2d.shape[0]):
        for mask_x in range(padded_mask_2d.shape[1]):
            if binned_mask_2d_mapper[mask_y, mask_x] == False:
                masked_array_1d_to_binned_masked_array_1d[binned_mask_index] = mask_index
                binned_mask_index += 1
            if padded_mask_2d[mask_y, mask_x] == False:
                mask_index += 1

    return masked_array_1d_to_binned_masked_array_1d