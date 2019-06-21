#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 17:39:42 2019

@author: Olegs Nikisins
"""

# =============================================================================
# Import what is needed here:

import numpy as np


# =============================================================================
# Main body:

def reshape_flat_patches(patches, patch_reshape_parameters = None):
    """
    Reshape a set of flattened patches into original dimensions, 2D or 3D

    **Parameters:**

    ``patches`` : 2D :py:class:`numpy.ndarray`
        An array containing flattened patches. The dimensions are:
        ``num_patches x len_of_flat_patch``

    ``patch_reshape_parameters`` : [int] or None
        The parameters to be used for patch reshaping. The loaded patch is
        vectorized. Example:
        ``patch_reshape_parameters = [4, 8, 8]``, then the patch of the
        size (256,) will be reshaped to (4,8,8) dimensions. Only 2D and 3D
        patches are supported.
        Default: None.

    **Returns:**

    ``patches_3d`` : [2D or 3D :py:class:`numpy.ndarray`]
        A list of patches converted to the original dimensions.
    """

    patches_3d = []

    for patch in patches:

        if patch_reshape_parameters is not None:

            # The dimensionality of the reshaped patch:
            new_shape = [np.int(len(patch)/(patch_reshape_parameters[-2]*patch_reshape_parameters[-1]))] + list(patch_reshape_parameters[-2:])

            patch = np.squeeze(patch.reshape(new_shape))

        patches_3d.append(patch)

    return patches_3d


# =============================================================================
def mean_std_patch_norm(patches, channel_means = None, channel_stds = None):
    """
    Apply mean-std normalization to the patches channel-wise.

    **Parameters:**

    ``patches`` : [2D or 3D :py:class:`numpy.ndarray`]
        A list of patches converted to the original dimensions.

    ``channel_means`` : [float] or None
        The channel-wise mean values to be used for mean-std normalization
        of the patches. Only normalization of 3D patches is currently
        supported.
        Default: None.

    ``channel_stds`` : [float] or None
        The channel-wise std values to be used for mean-std normalization
        of the patches. Only normalization of 3D patches is currently
        supported.
        Default: None.

    **Returns:**

    ``patches_norm_3d`` : [2D or 3D :py:class:`numpy.ndarray`]
        A list of patches normalized channel-wise.
    """

    patches_norm_3d = []

    for patch in patches:

        if channel_means is not None: # if normalization parameters are given

            patch = patch.astype(np.float) # convert to float for normalization

            if len(patch.shape) == 3: # Only normalization of 3D patches is currently handled

                for idx, patch_channel in enumerate(patch): # for all channels

                    patch[idx,:,:] = (patch_channel - channel_means[idx]) / channel_stds[idx]

        patches_norm_3d.append(patch)

    return patches_norm_3d


