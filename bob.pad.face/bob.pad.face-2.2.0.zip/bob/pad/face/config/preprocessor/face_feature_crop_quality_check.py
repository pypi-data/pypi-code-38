#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 13:53:58 2018

@author: Olegs Nikisins
"""

# =============================================================================
# Import here:

from bob.bio.base.preprocessor import Preprocessor

from bob.bio.video.preprocessor import Wrapper

import os

import importlib

from bob.pad.face.utils.patch_utils import reshape_flat_patches

from bob.bio.video.utils import FrameSelector

from bob.pad.face.preprocessor import BlockPatch


# =============================================================================
# define preprocessor class:

class _Preprocessor(Preprocessor):
    """
    The following steps are performed:

    1. Detect and align the face.

    2. Assess the quality of the face image.

    3. Extract patch / patches from the face.

    **Parameters:**

    ``face_crop_align`` : object
        An instance of the FaceCropAlign preprocessor to be used in step one.

    ``config_file``: py:class:`string`
        Relative name of the config file containing
        quality assessment function.
        Example: ``celeb_a/quality_assessment_config.py``.

    ``config_group``: py:class:`string`
        Group/package name containing the configuration file.
        Example: ``bob.pad.face.config.quality_assessment``.

    ``block_patch`` : object
        An instance of the BlockPatch preprocessor to be used in step 3.

    ``patch_reshape_parameters`` : [int] or None
        The parameters to be used for patch reshaping. The patch is
        vectorized. Example:
        ``patch_reshape_parameters = [4, 8, 8]``, then the patch of the
        size (256,) will be reshaped to (4,8,8) dimensions. Only 2D and 3D
        patches are supported.
        Default: None.

    ``patch_num`` : int OR None
        Am index of the patch to be selected from all extracted patches.
        Default: None
    """

    def __init__(self,
                 face_crop_align,
                 config_file,
                 config_group,
                 block_patch,
                 patch_reshape_parameters = None,
                 patch_num = None):

        super(_Preprocessor, self).__init__()

        self.face_crop_align = face_crop_align
        self.config_file = config_file
        self.config_group = config_group
        self.block_patch = block_patch
        self.patch_reshape_parameters = patch_reshape_parameters
        self.patch_num = patch_num


    def __call__(self, data, annotations):
        """
        **Parameters:**

        ``data`` : 2D or 3D :py:class:`numpy.ndarray`
            Input image (RGB or gray-scale) or None.

        ``annotations`` : :py:class:`dict` or None
            A dictionary containing annotations of the face bounding box.
            Dictionary must be as follows:
            ``{'topleft': (row, col), 'bottomright': (row, col)}``
            Default: None .
        """

        face_data = self.face_crop_align(data, annotations)

        if face_data is None:

            return None

        relative_mod_name = '.' + os.path.splitext(self.config_file)[0].replace(os.path.sep, '.')

        config_module = importlib.import_module(relative_mod_name, self.config_group)

        quality_flag = config_module.assess_quality(face_data, **config_module.assess_quality_kwargs)

        if quality_flag:

            print ("Good quality data.")

            patches = self.block_patch(face_data, annotations=None)

            if self.patch_reshape_parameters is not None:

                patches = reshape_flat_patches(patches, self.patch_reshape_parameters)

            if self.patch_num is not None:

                patches = patches[self.patch_num]

        else:

            print ("Bad quality data.")
            return None

        return patches


# =============================================================================
# define instance of the preprocessor:

"""
Preprocessor to be used for Color channel.
"""

from bob.pad.face.preprocessor import FaceCropAlign

FACE_SIZE = 128  # The size of the resulting face
RGB_OUTPUT_FLAG = True  # RGB output
USE_FACE_ALIGNMENT = True  # use annotations
MAX_IMAGE_SIZE = 1920  # no limiting here
FACE_DETECTION_METHOD = "mtcnn"  # DON'T use ANNOTATIONS, valid for CelebA only
MIN_FACE_SIZE = 50  # skip small faces

_face_crop_align = FaceCropAlign(face_size = FACE_SIZE,
                                 rgb_output_flag = RGB_OUTPUT_FLAG,
                                 use_face_alignment = USE_FACE_ALIGNMENT,
                                 max_image_size = MAX_IMAGE_SIZE,
                                 face_detection_method = FACE_DETECTION_METHOD,
                                 min_face_size = MIN_FACE_SIZE)

"""
Parameters to be used for quality assessment.
"""

CONFIG_FILE = "celeb_a/quality_assessment_config_128.py"

CONFIG_GROUP = "bob.pad.face.config.quality_assessment"

"""
Define an instance of the BlockPatch preprocessor.
"""

PATCH_SIZE = 64
STEP = 32

_block_patch = BlockPatch(patch_size = PATCH_SIZE,
                          step = STEP,
                          use_annotations_flag = False)

"""
define an instance of the _Preprocessor class.
"""

_frame_selector = FrameSelector(selection_style = "all")

_image_extractor_0 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 0)

face_feature_0_crop_rgb = Wrapper(preprocessor = _image_extractor_0,
                                  frame_selector = _frame_selector)


# =============================================================================
_image_extractor_1 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 1)

face_feature_1_crop_rgb = Wrapper(preprocessor = _image_extractor_1,
                                  frame_selector = _frame_selector)

# =============================================================================
_image_extractor_2 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 2)

face_feature_2_crop_rgb = Wrapper(preprocessor = _image_extractor_2,
                                  frame_selector = _frame_selector)

# =============================================================================
_image_extractor_3 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 3)

face_feature_3_crop_rgb = Wrapper(preprocessor = _image_extractor_3,
                                  frame_selector = _frame_selector)

# =============================================================================
_image_extractor_4 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 4)

face_feature_4_crop_rgb = Wrapper(preprocessor = _image_extractor_4,
                                  frame_selector = _frame_selector)

# =============================================================================
_image_extractor_5 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 5)

face_feature_5_crop_rgb = Wrapper(preprocessor = _image_extractor_5,
                                  frame_selector = _frame_selector)

# =============================================================================
_image_extractor_6 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 6)

face_feature_6_crop_rgb = Wrapper(preprocessor = _image_extractor_6,
                                  frame_selector = _frame_selector)

# =============================================================================
_image_extractor_7 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 7)

face_feature_7_crop_rgb = Wrapper(preprocessor = _image_extractor_7,
                                  frame_selector = _frame_selector)

# =============================================================================
_image_extractor_8 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 8)

face_feature_8_crop_rgb = Wrapper(preprocessor = _image_extractor_8,
                                  frame_selector = _frame_selector)

# =============================================================================
# Extractors for obtaining RGB patches of the size 3x32x32

PATCH_SIZE = 32
STEP = 32

_block_patch_32x32 = BlockPatch(patch_size = PATCH_SIZE,
                          step = STEP,
                          use_annotations_flag = False)

_image_extractor_0_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 0)

face_feature_0_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_0_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_1_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 1)

face_feature_1_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_1_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_2_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 2)

face_feature_2_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_2_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_3_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 3)

face_feature_3_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_3_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_4_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 4)

face_feature_4_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_4_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_5_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 5)

face_feature_5_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_5_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_6_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 6)

face_feature_6_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_6_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_7_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 7)

face_feature_7_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_7_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_8_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 8)

face_feature_8_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_8_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_9_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 9)

face_feature_9_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_9_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_10_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 10)

face_feature_10_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_10_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_11_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 11)

face_feature_11_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_11_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_12_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 12)

face_feature_12_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_12_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_13_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 13)

face_feature_13_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_13_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_14_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 14)

face_feature_14_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_14_32x32,
                                  frame_selector = _frame_selector)


_image_extractor_15_32x32 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_32x32,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 15)

face_feature_15_32x32_crop_rgb = Wrapper(preprocessor = _image_extractor_15_32x32,
                                  frame_selector = _frame_selector)


# =============================================================================
# Extractors for obtaining RGB patches (patch is an entire face in this case) of the size 3x128x128

PATCH_SIZE = 128
STEP = 1

_block_patch_128x128 = BlockPatch(patch_size = PATCH_SIZE,
                          step = STEP,
                          use_annotations_flag = False)

_image_extractor_0_128x128 = _Preprocessor(face_crop_align = _face_crop_align,
                                   config_file = CONFIG_FILE,
                                   config_group = CONFIG_GROUP,
                                   block_patch = _block_patch_128x128,
                                   patch_reshape_parameters = [3, PATCH_SIZE, PATCH_SIZE],
                                   patch_num = 0)

face_feature_0_128x128_crop_rgb = Wrapper(preprocessor = _image_extractor_0_128x128,
                                  frame_selector = _frame_selector)



