#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 14:14:28 2018

@author: Olegs Nikisins
"""

# =============================================================================
# Import what is needed here:

from bob.bio.base.preprocessor import Preprocessor

import numpy as np


# =============================================================================
class BlockPatch(Preprocessor, object):
    """
    This class is designed to extract patches from the ROI in the input image.
    The ROI/block to extract patches from is defined by the top-left and
    bottom-right coordinates of the bounding box. Patches can be extracted
    from the loactions of the nodes of the uniform grid.
    Size of the grid cell is defined by the step parameter.
    Patches are of the square shape, and the number of extracted patches is
    equal to the number of nodes. All possible patches will be extracted from
    the ROI. If ROI is not defined, the entire image will be considered as ROI.

    **Parameters:**

    ``patch_size`` : :py:class:`int`
        The size of the square patch to extract from image.
        The dimensionality of extracted patches:
        ``num_channels x patch_size x patch_size``, where ``num_channels`` is
        the number of channels in the input image.

    ``step`` : :py:class:`int`
        Defines the size of the cell of the uniform grid to extract patches
        from. Patches will be extracted from the locations of the grid nodes.

    ``use_annotations_flag`` : bool
        A flag defining if annotations should be used in the call method.
        If ``False``, patches from the whole image will be extracted.
        If ``True``, patches from the ROI defined by the annotations will be
        extracted,
        Default: True.
    """

    # ==========================================================================
    def __init__(self, patch_size,
                 step,
                 use_annotations_flag = True):

        super(BlockPatch, self).__init__(patch_size=patch_size,
                                         step=step,
                                         use_annotations_flag=use_annotations_flag)

        self.patch_size = patch_size
        self.step = step
        self.use_annotations_flag = use_annotations_flag


    # ==========================================================================
    def __call__(self, image, annotations=None):
        """
        This class is designed to extract patches from the ROI in the input
        image. ROI is defined by the ``annotations`` argument. If
        annotations are not given, patches will be extracted from the whole
        image.

        **Parameters:**

        ``image`` : 2D to ND :py:class:`numpy.ndarray`
            Input image (gray-scale, RGB or multi-spectral).
            The expected dimensionality of the image is:
            ``num_channels x w x h``.

        ``annotations`` : [] or None
            A list containing annotations of bounding box defining ROI.
            ``annotations[0] = [x_top_left, y_top_left]``
            ``annotations[1] = [x_bottom_right, y_bottom_right]``
            Non-integer annotations are also allowed.

        **Returns:**

        ``patches_array`` : 2D :py:class:`numpy.ndarray`
            An array containing flattened patches. To get a list of patches
            with original dimensions you can do the following:
            ``patches_reconstructed = [patch.reshape(n_channels, patch_size, patch_size) for patch in patches_array]``.
        """

        if not self.use_annotations_flag:

            annotations = None # don't use annotations

        """
        Get the ROI:
        """
        if annotations is not None:

            x1 = np.max([0, np.int(annotations[0][0])])
            x2 = np.min([np.int(annotations[1][0]), image.shape[-1]])
            y1 = np.max([0, np.int(annotations[0][1])])
            y2 = np.min([np.int(annotations[1][1]), image.shape[-2]])

            if len(image.shape) == 2: # for gray-scale images

                roi = image[y1:y2, x1:x2]

            elif len(image.shape) == 3: # for multi-spectral images

                roi = image[:,y1:y2, x1:x2]

            else: # input data of higher dimensions is not handled

                return None

        else: # if annotations are not defined

            roi = image

        """
        Get patches from ROI:
        """
        n_blocks_x = np.int((roi.shape[-1] - self.patch_size)/self.step + 1) # Number of full patches horizontally
        n_blocks_y = np.int((roi.shape[-2] - self.patch_size)/self.step + 1) # Number of full patches vertically

        patch_indices_x = np.arange(n_blocks_x)*self.step # Horizontal starting indices of the patches
        patch_indices_y = np.arange(n_blocks_y)*self.step # Vorizontal starting indices of the patches

        # Function to get vertical blocks from image, given starting indices of the blocks:
        get_vert_block = lambda im, x_vec : [im[:, x:x+self.patch_size] if len(im.shape)==2 else im[:, :, x:x+self.patch_size] for x in x_vec]

        # Function to get horizontal blocks from image, given starting indices of the blocks:
        get_hor_block = lambda im, y_vec : [im[y:y+self.patch_size, :] if len(im.shape)==2 else im[:, y:y+self.patch_size, :] for y in y_vec]

        # Get all the patches from ROI, patches are returned row-wise:
        patches = [hor_block for vert_block in get_vert_block(roi, patch_indices_x) for hor_block in get_hor_block(vert_block, patch_indices_y)]

        if not patches: # if no patches can be computed
            return None

        patches_array = np.vstack([np.ndarray.flatten(patch) for patch in patches])

        return patches_array


