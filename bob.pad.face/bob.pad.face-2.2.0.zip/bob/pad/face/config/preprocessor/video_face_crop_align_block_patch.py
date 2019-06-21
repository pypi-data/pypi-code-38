#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# =============================================================================
# Import here:
from bob.pad.face.preprocessor import VideoFaceCropAlignBlockPatch

from bob.pad.face.preprocessor import FaceCropAlign

from bob.bio.video.preprocessor import Wrapper

from bob.bio.video.utils import FrameSelector

from bob.pad.face.preprocessor.FaceCropAlign import auto_norm_image as _norm_func

from bob.pad.face.preprocessor import BlockPatch


# =============================================================================
# names of the channels to process:
_channel_names = ['color', 'infrared', 'depth']


# =============================================================================
# dictionary containing preprocessors for all channels:
_preprocessors = {}

"""
Preprocessor to be used for Color channel.
"""
FACE_SIZE = 128  # The size of the resulting face
RGB_OUTPUT_FLAG = False  # BW output
USE_FACE_ALIGNMENT = True  # use annotations
MAX_IMAGE_SIZE = None  # no limiting here
FACE_DETECTION_METHOD = None  # use ANNOTATIONS
MIN_FACE_SIZE = 50  # skip small faces

_image_preprocessor = FaceCropAlign(face_size = FACE_SIZE,
                                    rgb_output_flag = RGB_OUTPUT_FLAG,
                                    use_face_alignment = USE_FACE_ALIGNMENT,
                                    max_image_size = MAX_IMAGE_SIZE,
                                    face_detection_method = FACE_DETECTION_METHOD,
                                    min_face_size = MIN_FACE_SIZE)

_frame_selector = FrameSelector(selection_style = "all")

_preprocessor_rgb = Wrapper(preprocessor = _image_preprocessor,
                            frame_selector = _frame_selector)

_preprocessors[_channel_names[0]] = _preprocessor_rgb

"""
Preprocessor to be used for Infrared (or Thermal) channels:
"""
FACE_SIZE = 128  # The size of the resulting face
RGB_OUTPUT_FLAG = False  # Gray-scale output
USE_FACE_ALIGNMENT = True  # use annotations
MAX_IMAGE_SIZE = None  # no limiting here
FACE_DETECTION_METHOD = None  # use annotations
MIN_FACE_SIZE = 50  # skip small faces
NORMALIZATION_FUNCTION = _norm_func
NORMALIZATION_FUNCTION_KWARGS = {}
NORMALIZATION_FUNCTION_KWARGS = {'n_sigma':3.0, 'norm_method':'MAD'}

_image_preprocessor_ir = FaceCropAlign(face_size = FACE_SIZE,
                                    rgb_output_flag = RGB_OUTPUT_FLAG,
                                    use_face_alignment = USE_FACE_ALIGNMENT,
                                    max_image_size = MAX_IMAGE_SIZE,
                                    face_detection_method = FACE_DETECTION_METHOD,
                                    min_face_size = MIN_FACE_SIZE,
                                    normalization_function = NORMALIZATION_FUNCTION,
                                    normalization_function_kwargs = NORMALIZATION_FUNCTION_KWARGS)

_preprocessor_ir = Wrapper(preprocessor = _image_preprocessor_ir,
                               frame_selector = _frame_selector)

_preprocessors[_channel_names[1]] = _preprocessor_ir

"""
Preprocessor to be used for Depth channel:
"""
FACE_SIZE = 128  # The size of the resulting face
RGB_OUTPUT_FLAG = False  # Gray-scale output
USE_FACE_ALIGNMENT = True  # use annotations
MAX_IMAGE_SIZE = None  # no limiting here
FACE_DETECTION_METHOD = None  # use annotations
MIN_FACE_SIZE = 50  # skip small faces
NORMALIZATION_FUNCTION = _norm_func
NORMALIZATION_FUNCTION_KWARGS = {}
NORMALIZATION_FUNCTION_KWARGS = {'n_sigma':6.0, 'norm_method':'MAD'}

_image_preprocessor_d = FaceCropAlign(face_size = FACE_SIZE,
                                    rgb_output_flag = RGB_OUTPUT_FLAG,
                                    use_face_alignment = USE_FACE_ALIGNMENT,
                                    max_image_size = MAX_IMAGE_SIZE,
                                    face_detection_method = FACE_DETECTION_METHOD,
                                    min_face_size = MIN_FACE_SIZE,
                                    normalization_function = NORMALIZATION_FUNCTION,
                                    normalization_function_kwargs = NORMALIZATION_FUNCTION_KWARGS)

_preprocessor_d = Wrapper(preprocessor = _image_preprocessor_d,
                               frame_selector = _frame_selector)

_preprocessors[_channel_names[2]] = _preprocessor_d


# =============================================================================
# define parameters and an instance of the patch extractor:
PATCH_SIZE = 128
STEP = 1

_block_patch_128x128 = BlockPatch(patch_size = PATCH_SIZE,
                                  step = STEP,
                                  use_annotations_flag = False)


# =============================================================================
"""
Define an instance for extraction of one (**whole face**) multi-channel
(BW-NIR-D) face patch of the size (3 x 128 x 128).
"""
video_face_crop_align_bw_ir_d_channels_3x128x128 = VideoFaceCropAlignBlockPatch(preprocessors = _preprocessors,
                                                                                channel_names = _channel_names,
                                                                                return_multi_channel_flag = True,
                                                                                block_patch_preprocessor = _block_patch_128x128)

# This instance is similar to above, but will return a **vectorized** patch:
video_face_crop_align_bw_ir_d_channels_3x128x128_vect = VideoFaceCropAlignBlockPatch(preprocessors = _preprocessors,
                                                                                     channel_names = _channel_names,
                                                                                     return_multi_channel_flag = False,
                                                                                     block_patch_preprocessor = _block_patch_128x128)
