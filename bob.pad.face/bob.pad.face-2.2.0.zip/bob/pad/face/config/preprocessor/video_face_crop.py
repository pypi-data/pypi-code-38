#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from bob.pad.face.preprocessor import FaceCropAlign

from bob.bio.video.preprocessor import Wrapper

from bob.bio.video.utils import FrameSelector

# =======================================================================================
# Define instances here:


FACE_SIZE = 64  # The size of the resulting face
RGB_OUTPUT_FLAG = True  # RGB output
USE_FACE_ALIGNMENT = False  #
MAX_IMAGE_SIZE = None  # no limiting here
FACE_DETECTION_METHOD = "dlib"  # use dlib face detection
MIN_FACE_SIZE = 50  # skip small faces

_image_preprocessor = FaceCropAlign(face_size=FACE_SIZE,
                                    rgb_output_flag=RGB_OUTPUT_FLAG,
                                    use_face_alignment=USE_FACE_ALIGNMENT,
                                    max_image_size=MAX_IMAGE_SIZE,
                                    face_detection_method=FACE_DETECTION_METHOD,
                                    min_face_size=MIN_FACE_SIZE)

_frame_selector = FrameSelector(selection_style = "all")

rgb_face_detector_dlib = Wrapper(preprocessor = _image_preprocessor,
                                 frame_selector = _frame_selector)

# =======================================================================================
FACE_DETECTION_METHOD = "mtcnn"  # use mtcnn face detection

_image_preprocessor = FaceCropAlign(face_size=FACE_SIZE,
                                    rgb_output_flag=RGB_OUTPUT_FLAG,
                                    use_face_alignment=USE_FACE_ALIGNMENT,
                                    max_image_size=MAX_IMAGE_SIZE,
                                    face_detection_method=FACE_DETECTION_METHOD,
                                    min_face_size=MIN_FACE_SIZE)

rgb_face_detector_mtcnn = Wrapper(preprocessor = _image_preprocessor,
                                  frame_selector = _frame_selector)

# =======================================================================================
FACE_SIZE = 64  # The size of the resulting face
RGB_OUTPUT_FLAG = False  # Gray-scale output
USE_FACE_ALIGNMENT = True  # detect face landmarks locally and align the face
MAX_IMAGE_SIZE = 1920  # the largest possible dimension of the input image
FACE_DETECTION_METHOD = "mtcnn"  # face landmarks detection method
MIN_FACE_SIZE = 50  # skip faces smaller than this value
NORMALIZATION_FUNCTION = None  # no normalization
NORMALIZATION_FUNCTION_KWARGS = None

_image_preprocessor = FaceCropAlign(face_size=FACE_SIZE,
                                    rgb_output_flag=RGB_OUTPUT_FLAG,
                                    use_face_alignment=USE_FACE_ALIGNMENT,
                                    max_image_size=MAX_IMAGE_SIZE,
                                    face_detection_method=FACE_DETECTION_METHOD,
                                    min_face_size=MIN_FACE_SIZE,
                                    normalization_function=NORMALIZATION_FUNCTION,
                                    normalization_function_kwargs=NORMALIZATION_FUNCTION_KWARGS)

bw_face_detect_mtcnn = Wrapper(preprocessor=_image_preprocessor,
                               frame_selector=_frame_selector)
