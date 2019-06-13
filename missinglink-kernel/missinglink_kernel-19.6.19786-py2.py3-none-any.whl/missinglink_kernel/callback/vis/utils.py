from __future__ import division

from collections import Iterable

import numpy as np

# Globals
_CLASS_INDEX = None


def reverse_enumerate(iterable):
    """Enumerate over an iterable in reverse order while retaining proper indexes, without creating any copies.
    """
    return zip(reversed(range(len(iterable))), reversed(iterable))


def listify(value):
    """Ensures that the value is a list. If it is not a list, it creates a new list with `value` as an item within it.
    """
    if not isinstance(value, Iterable):
        value = [value]

    return value


def get_img_shape(img, K):
    if K.image_dim_ordering() == 'th':
        return K.int_shape(img)
    else:
        samples, rows, cols, ch = K.int_shape(img)
        return samples, ch, rows, cols


def get_img_indices(dim_ordering):
    """Returns image indices in a backend agnostic manner.

    Returns:
        A tuple representing indices for image in `(samples, channels, rows, cols)` order.
    """
    if dim_ordering == 'th':
        return 0, 1, 2, 3
    else:
        return 0, 3, 1, 2


def deprocess_image(img):
    """Utility function to convert optimized image output into a valid image.
    Args:
        img: 3D numpy array with shape: `(channels, rows, cols)` if dim_ordering='th' or
            `(rows, cols, channels)` if dim_ordering='tf'.
    Returns:
        A valid image output.
    """
    # normalize tensor: center on 0., ensure std is 0.1
    img -= img.mean()
    img /= (img.std() + 1e-5)
    img *= 0.1

    # clip to [0, 1]
    img += 0.5
    img = np.clip(img, 0, 1)

    # convert to RGB array
    img *= 255

    # TF image format if channels = (1 or 3) towards the last rank.
    if img.shape[-1] != 3 and img.shape[-1] != 1:
        img = img.transpose((1, 2, 0))

    img = np.clip(img, 0, 255).astype('uint8')
    return img


class _BackendAgnosticImageSlice(object):
    def __init__(self, dim_ordering):
        self.dim_ordering = dim_ordering

    def __getitem__(self, item_slice):
        """Assuming a slice for shape `(samples, channels, width, height)`
        """
        assert len(item_slice) == 4
        if self.dim_ordering == 'th':
            return item_slice
        else:
            return tuple([item_slice[0], item_slice[2], item_slice[3], item_slice[1]])


def slicer(dim_ordering):
    return _BackendAgnosticImageSlice(dim_ordering)
