#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""Test Units
"""
#==============================================================================
# Import what is needed here:
import numpy as np

from bob.io.base.test_utils import datafile

from bob.io.base import load

import bob.io.image  # for image loading functionality

import bob.bio.video

from bob.ip.color import rgb_to_gray

from ..extractor import LBPHistogram

from ..preprocessor import FaceCropAlign

from ..preprocessor import FrameDifference

from ..extractor import FrameDiffFeatures

from ..extractor import LBPHistogram

from ..extractor import ImageQualityMeasure

from ..preprocessor import LiPulseExtraction
from ..preprocessor import Chrom
from ..preprocessor import PPGSecure as PPGPreprocessor
from ..preprocessor import SSR

from ..extractor import LTSS
from ..extractor import LiSpectralFeatures
from ..extractor import PPGSecure as PPGExtractor


from ..preprocessor.FaceCropAlign import detect_face_landmarks_in_image

from bob.bio.video.preprocessor import Wrapper

from ..preprocessor import VideoFaceCropAlignBlockPatch

from bob.bio.video.utils import FrameSelector

from ..preprocessor import BlockPatch

from bob.pad.face.config.preprocessor.face_feature_crop_quality_check import face_feature_0_128x128_crop_rgb

from bob.pad.face.utils.patch_utils import reshape_flat_patches

from bob.pad.face.config.preprocessor.video_face_crop_align_block_patch import video_face_crop_align_bw_ir_d_channels_3x128x128 as mc_preprocessor


def test_detect_face_landmarks_in_image_mtcnn():

    img = load(datafile('testimage.jpg', 'bob.bio.face.test'))
    assert len(img) == 3
    annotations = detect_face_landmarks_in_image(
        img, method='mtcnn')
    assert len(annotations['landmarks']) == 68
    assert len(annotations['leye']) == 2
    assert len(annotations['reye']) == 2
    assert len(annotations['topleft']) == 2
    assert len(annotations['bottomright']) == 2

    #assert len(annotations['leye']) == (176, 220)


def test_detect_face_landmarks_in_image_dlib():

    img = load(datafile('testimage.jpg', 'bob.bio.face.test'))
    assert len(img) == 3
    annotations = detect_face_landmarks_in_image(
        img, method='dlib')
    assert len(annotations['landmarks']) == 68
    assert len(annotations['leye']) == 2
    assert len(annotations['reye']) == 2
    assert len(annotations['topleft']) == 2
    assert len(annotations['bottomright']) == 2

    #assert len(annotations['leye']) == (176, 220)


#==============================================================================
def test_lbp_histogram():
    lbp = LBPHistogram()
    img = load(datafile('testimage.jpg', 'bob.bio.face.test'))
    img = rgb_to_gray(img)
    features = lbp(img)
    reference = load(datafile('lbp.hdf5', 'bob.pad.face.test'))
    assert np.allclose(features, reference)


#==============================================================================
def test_face_crop_align():
    """
    Test FaceCropAlign preprocessor, which is designed to crop faces in the images.
    """

    image = load(datafile('test_image.png', 'bob.pad.face.test'))
    annotations = {'topleft': (95, 155), 'bottomright': (215, 265)}

    preprocessor = FaceCropAlign(face_size=64, rgb_output_flag=False, use_face_alignment=False)
    face = preprocessor(image, annotations)

    assert face.shape == (64, 64)
    assert np.sum(face) == 429158

    preprocessor = FaceCropAlign(face_size=64, rgb_output_flag=True, use_face_alignment=False)
    face = preprocessor(image, annotations)

    assert face.shape == (3, 64, 64)
    assert np.sum(face) == 1215525


#==============================================================================
def convert_image_to_video_data(image, annotations, n_frames):
    """
    Convert input image to video and image annotations to frame annotations.

    **Parameters:**

    ``image`` : 2D or 3D :py:class:`numpy.ndarray`
        Input image (RGB or gray-scale).

    ``annotations`` : :py:class:`dict`
        A dictionary containing annotations of the face bounding box.
        Dictionary must be as follows ``{'topleft': (row, col), 'bottomright': (row, col)}``

    ``n_frames`` : :py:class:`int`
        Number of frames in the output video

    **Returns:**

    ``frame_container`` : FrameContainer
        Video data stored in the FrameContainer, see ``bob.bio.video.utils.FrameContainer``
        for further details.

    ``video_annotations`` : :py:class:`dict`
        A dictionary containing the annotations for each frame in the video.
        Dictionary structure: ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.
        Where ``frameN_dict = {'topleft': (row, col), 'bottomright': (row, col)}``
        is the dictionary defining the coordinates of the face bounding box in frame N.
    """

    frame_container = bob.bio.video.FrameContainer(
    )  # initialize the FrameContainer

    video_annotations = {}

    for idx, fn in enumerate(range(0, n_frames)):

        frame_container.add(idx, image)  # add current frame to FrameContainer

        video_annotations[str(idx)] = annotations

    return frame_container, video_annotations


#==============================================================================
def test_video_face_crop():
    """
    Test FaceCropAlign preprocessor with Wrapper, which is designed to crop faces in the video.
    """

    FACE_SIZE = 64 # The size of the resulting face
    RGB_OUTPUT_FLAG = False # Gray-scale output
    USE_FACE_ALIGNMENT = False # use annotations
    MAX_IMAGE_SIZE = None # no limiting here
    FACE_DETECTION_METHOD = None # use annotations
    MIN_FACE_SIZE = 50 # skip small faces

    image_preprocessor = FaceCropAlign(face_size = FACE_SIZE,
                                       rgb_output_flag = RGB_OUTPUT_FLAG,
                                       use_face_alignment = USE_FACE_ALIGNMENT,
                                       max_image_size = MAX_IMAGE_SIZE,
                                       face_detection_method = FACE_DETECTION_METHOD,
                                       min_face_size = MIN_FACE_SIZE)

    preprocessor = Wrapper(image_preprocessor)

    image = load(datafile('test_image.png', 'bob.pad.face.test'))
    annotations = {'topleft': (95, 155), 'bottomright': (215, 265)}

    video, annotations = convert_image_to_video_data(image, annotations, 20)

    faces = preprocessor(frames=video, annotations=annotations)

    assert len(faces) == 20
    assert faces[0][1].shape == (64, 64)
    assert faces[-1][1].shape == (64, 64)
    assert np.sum(faces[0][1]) == 429158
    assert np.sum(faces[-1][1]) == 429158

    #==========================================================================
    # test another configuration of the preprocessor:

    FACE_SIZE = 64 # The size of the resulting face
    RGB_OUTPUT_FLAG = True # Gray-scale output
    USE_FACE_ALIGNMENT = False # use annotations
    MAX_IMAGE_SIZE = None # no limiting here
    FACE_DETECTION_METHOD = "dlib" # use annotations
    MIN_FACE_SIZE = 50 # skip small faces

    image_preprocessor = FaceCropAlign(face_size = FACE_SIZE,
                                       rgb_output_flag = RGB_OUTPUT_FLAG,
                                       use_face_alignment = USE_FACE_ALIGNMENT,
                                       max_image_size = MAX_IMAGE_SIZE,
                                       face_detection_method = FACE_DETECTION_METHOD,
                                       min_face_size = MIN_FACE_SIZE)

    preprocessor = Wrapper(image_preprocessor)

    video, _ = convert_image_to_video_data(image, annotations, 3)

    faces = preprocessor(frames=video, annotations=annotations)

    assert len(faces) == 3
    assert faces[0][1].shape == (3, 64, 64)
    assert faces[-1][1].shape == (3, 64, 64)
    assert np.sum(faces[0][1]) == 1238664
    assert np.sum(faces[-1][1]) == 1238664

# =============================================================================
def test_video_face_crop_align_block_patch():
    """
    Test VideoFaceCropAlignBlockPatch preprocessor.
    """

    # =========================================================================
    # prepare the test data:

    image = load(datafile('test_image.png', 'bob.pad.face.test'))

    annotations = None

    video, annotations = convert_image_to_video_data(image, annotations, 2)

    mc_video = {}
    mc_video["color_1"] = video
    mc_video["color_2"] = video
    mc_video["color_3"] = video

    # =========================================================================
    # Initialize the VideoFaceCropAlignBlockPatch.

    # names of the channels to process:
    _channel_names = ['color_1', 'color_2', 'color_3']

    # dictionary containing preprocessors for all channels:
    _preprocessors = {}

    """
    All channels are color, so preprocessors for all of them are identical.
    """
    FACE_SIZE = 128  # The size of the resulting face
    RGB_OUTPUT_FLAG = False  # BW output
    USE_FACE_ALIGNMENT = True  # use annotations
    MAX_IMAGE_SIZE = None  # no limiting here
    FACE_DETECTION_METHOD = "mtcnn"  # use ANNOTATIONS
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
    _preprocessors[_channel_names[1]] = _preprocessor_rgb
    _preprocessors[_channel_names[2]] = _preprocessor_rgb

    """
    The instance of the BlockPatch preprocessor.
    """

    PATCH_SIZE = 64
    STEP = 32

    _block_patch = BlockPatch(patch_size = PATCH_SIZE,
                              step = STEP,
                              use_annotations_flag = False)

    preprocessor = VideoFaceCropAlignBlockPatch(preprocessors = _preprocessors,
                                                channel_names = _channel_names,
                                                return_multi_channel_flag = True,
                                                block_patch_preprocessor = _block_patch)

    # =========================================================================
    # pre-process the data and assert the result:

    data_preprocessed = preprocessor(frames = mc_video, annotations = annotations)

    assert len(data_preprocessed) == 2
    assert data_preprocessed[0][1].shape == (3, 128, 128)
    assert data_preprocessed[1][1].shape == (3, 128, 128)

    preprocessor.return_multi_channel_flag = False # now extract patches

    data_preprocessed = preprocessor(frames = mc_video, annotations = annotations)

    assert len(data_preprocessed) == 2
    assert data_preprocessed[0][1].shape == (9, 12288)
    assert data_preprocessed[1][1].shape == (9, 12288)


# =============================================================================
def test_preproc_with_quality_check():
    """
    Test _Preprocessor cropping the face and checking the quality of the image
    applying eye detection, and asserting if they are in the expected positions.
    """

    # =========================================================================
    # prepare the test data:
    image = load(datafile('test_image.png', 'bob.pad.face.test'))

    annotations = None

    video, annotations = convert_image_to_video_data(image, annotations, 2)

    # =========================================================================
    # test the preprocessor:
    data_preprocessed = face_feature_0_128x128_crop_rgb(video)

    assert data_preprocessed is None


# =============================================================================
def test_multi_channel_preprocessing():
    """
    Test video_face_crop_align_bw_ir_d_channels_3x128x128 preprocessor.
    """

    # =========================================================================
    # prepare the test data:

    image = load(datafile('test_image.png', 'bob.pad.face.test'))

    # annotations must be known for this preprocessor, so compute them:
    annotations = detect_face_landmarks_in_image(image, method="mtcnn")

    video_color, annotations = convert_image_to_video_data(image, annotations, 2)

    video_bw, _ = convert_image_to_video_data(image[0], annotations, 2)

    mc_video = {}
    mc_video["color"] = video_color
    mc_video["infrared"] = video_bw
    mc_video["depth"] = video_bw

    # =========================================================================
    # test the preprocessor:

    data_preprocessed = mc_preprocessor(mc_video, annotations)

    assert len(data_preprocessed) == 2
    assert data_preprocessed[0][1].shape == (3, 128, 128)

    # chanenls are preprocessed differently, thus this should apply:
    assert np.any(data_preprocessed[0][1][0] != data_preprocessed[0][1][1])
    assert np.any(data_preprocessed[0][1][0] != data_preprocessed[0][1][2])


# =============================================================================
def test_reshape_flat_patches():
    """
    Test reshape_flat_patches function.
    """

    image = load(datafile('test_image.png', 'bob.pad.face.test'))

    patch1 = image[0,0:10,0:10]
    patch2 = image[1,0:10,0:10]

    patches = np.stack([patch1.flatten(), patch2.flatten()])
    patches_3d = reshape_flat_patches(patches, (10, 10))

    assert np.all(patch1 == patches_3d[0])
    assert np.all(patch2 == patches_3d[1])

    # =========================================================================
    patch1 = image[:,0:10,0:10]
    patch2 = image[:,1:11,1:11]

    patches = np.stack([patch1.flatten(), patch2.flatten()])
    patches_3d = reshape_flat_patches(patches, (3, 10, 10))

    assert np.all(patch1 == patches_3d[0])
    assert np.all(patch2 == patches_3d[1])


#==============================================================================
def test_frame_difference():
    """
    Test FrameDifference preprocessor computing frame differences for both
    facial and non-facial/background regions.
    """

    image = load(datafile('test_image.png', 'bob.pad.face.test'))
    annotations = {'topleft': (95, 155), 'bottomright': (215, 265)}

    n_frames = 20

    video, annotations = convert_image_to_video_data(image, annotations,
                                                     n_frames)

    NUMBER_OF_FRAMES = None  # process all frames
    CHECK_FACE_SIZE_FLAG = True  # Check size of the face
    MIN_FACE_SIZE = 50  # Minimal size of the face to consider

    preprocessor = FrameDifference(
        number_of_frames=NUMBER_OF_FRAMES,
        check_face_size_flag=CHECK_FACE_SIZE_FLAG,
        min_face_size=MIN_FACE_SIZE)

    diff = preprocessor(frames=video, annotations=annotations)

    assert diff.shape == (n_frames - 1, 2)
    assert (diff == 0).all()


#==============================================================================
def test_frame_diff_features():
    """
    Test FrameDiffFeatures extractor computing 10 features given frame differences.
    """

    WINDOW_SIZE = 20
    OVERLAP = 0

    extractor = FrameDiffFeatures(window_size=WINDOW_SIZE, overlap=OVERLAP)

    data = np.transpose(np.vstack([range(0, 100), range(0, 100)]))

    features = extractor(data)

    assert len(features) == 5
    assert len(features[0][1]) == 10
    assert len(features[-1][1]) == 10
    assert (features[0][1][0:5] == features[0][1][5:]).all()
    assert (np.sum(features[0][1]) - 73.015116873109207) < 0.000001


#==============================================================================
def test_video_lbp_histogram():
    """
    Test LBPHistogram with Wrapper extractor.
    """

    from ..preprocessor import FaceCropAlign

    from bob.bio.video.preprocessor import Wrapper

    FACE_SIZE = 64 # The size of the resulting face
    RGB_OUTPUT_FLAG = False # Gray-scale output
    USE_FACE_ALIGNMENT = False # use annotations
    MAX_IMAGE_SIZE = None # no limiting here
    FACE_DETECTION_METHOD = None # use annotations
    MIN_FACE_SIZE = 50 # skip small faces

    image_preprocessor = FaceCropAlign(face_size = FACE_SIZE,
                                       rgb_output_flag = RGB_OUTPUT_FLAG,
                                       use_face_alignment = USE_FACE_ALIGNMENT,
                                       max_image_size = MAX_IMAGE_SIZE,
                                       face_detection_method = FACE_DETECTION_METHOD,
                                       min_face_size = MIN_FACE_SIZE)

    preprocessor = Wrapper(image_preprocessor)

    image = load(datafile('test_image.png', 'bob.pad.face.test'))
    annotations = {'topleft': (95, 155), 'bottomright': (215, 265)}

    video, annotations = convert_image_to_video_data(image, annotations, 20)

    faces = preprocessor(frames=video, annotations=annotations)

    LBPTYPE = 'uniform'
    ELBPTYPE = 'regular'
    RAD = 1
    NEIGHBORS = 8
    CIRC = False
    DTYPE = None

    extractor = bob.bio.video.extractor.Wrapper(LBPHistogram(
        lbptype=LBPTYPE,
        elbptype=ELBPTYPE,
        rad=RAD,
        neighbors=NEIGHBORS,
        circ=CIRC,
        dtype=DTYPE))

    lbp_histograms = extractor(faces)

    assert len(lbp_histograms) == 20
    assert len(lbp_histograms[0][1]) == 59
    assert (lbp_histograms[0][1] == lbp_histograms[-1][1]).all()
    assert (lbp_histograms[0][1][0] - 0.12695109261186263) < 0.000001
    assert (lbp_histograms[0][1][-1] - 0.031737773152965658) < 0.000001


#==============================================================================
def test_video_quality_measure():
    """
    Test ImageQualityMeasure with Wrapper extractor.
    """

    image = load(datafile('test_image.png', 'bob.pad.face.test'))
    annotations = {'topleft': (95, 155), 'bottomright': (215, 265)}

    video, annotations = convert_image_to_video_data(image, annotations, 2)

    GALBALLY = True
    MSU = True
    DTYPE = None

    extractor = bob.bio.video.extractor.Wrapper(ImageQualityMeasure(galbally=GALBALLY, msu=MSU, dtype=DTYPE))

    features = extractor(video)

    assert len(features) == 2
    assert len(features[0][1]) == 139
    assert (features[0][1] == features[-1][1]).all()
    assert (features[0][1][0] - 2.7748559659812599e-05) < 0.000001
    assert (features[0][1][-1] - 0.16410418866596271) < 0.000001


#==============================================================================
def convert_array_to_list_of_frame_cont(data):
    """
    Convert an input 2D array to a list of FrameContainers.

    **Parameters:**

    ``data`` : 2D :py:class:`numpy.ndarray`
        Input data array of the dimensionality (N_samples X N_features ).

        **Returns:**

    ``frame_container_list`` : [FrameContainer]
        A list of FrameContainers, see ``bob.bio.video.utils.FrameContainer``
        for further details. Each frame container contains one feature vector.
    """

    frame_container_list = []

    for idx, vec in enumerate(data):

        frame_container = bob.bio.video.FrameContainer(
        )  # initialize the FrameContainer

        frame_container.add(0, vec)

        frame_container_list.append(
            frame_container)  # add current frame to FrameContainer

    return frame_container_list


def test_preprocessor_LiPulseExtraction():
      """ Test the pulse extraction using Li's ICPR 2016 algorithm.
      """

      image = load(datafile('test_image.png', 'bob.pad.face.test'))
      annotations = {'topleft': (95, 155), 'bottomright': (215, 265)}
      video, annotations = convert_image_to_video_data(image, annotations, 100)

      preprocessor = LiPulseExtraction(debug=False)
      pulse = preprocessor(video, annotations)
      assert pulse.shape == (100, 3)


def test_preprocessor_Chrom():
      """ Test the pulse extraction using CHROM algorithm.
      """

      image = load(datafile('test_image.png', 'bob.pad.face.test'))
      annotations = {'topleft': (95, 155), 'bottomright': (215, 265)}
      video, annotations = convert_image_to_video_data(image, annotations, 100)

      preprocessor = Chrom(debug=False)
      pulse = preprocessor(video, annotations)
      assert pulse.shape[0] == 100


def test_preprocessor_PPGSecure():
      """ Test the pulse extraction using PPGSecure algorithm.
      """

      image = load(datafile('test_image.png', 'bob.pad.face.test'))
      annotations = {'topleft': (456, 212), 'bottomright': (770, 500)}
      video, annotations = convert_image_to_video_data(image, annotations, 100)

      preprocessor = PPGPreprocessor(debug=False)
      pulse = preprocessor(video, annotations)
      assert pulse.shape == (100, 5)


def test_preprocessor_SSR():
      """ Test the pulse extraction using SSR algorithm.
      """

      image = load(datafile('test_image.png', 'bob.pad.face.test'))
      annotations = {'topleft': (95, 155), 'bottomright': (215, 265)}
      video, annotations = convert_image_to_video_data(image, annotations, 100)

      preprocessor = SSR(debug=False)
      pulse = preprocessor(video, annotations)
      assert pulse.shape[0] == 100


def test_extractor_LTSS():
      """ Test Long Term Spectrum Statistics (LTSS) Feature Extractor
      """

      # "pulse" in 3 color channels
      data = np.random.random((200, 3))

      extractor = LTSS(concat=True)
      features = extractor(data)
      # n = number of FFT coefficients (default is 64)
      # (n/2 + 1) * 2 (mean and std) * 3 (colors channels)
      assert features.shape[0] == 33*2*3

      extractor = LTSS(concat=False)
      features = extractor(data)
      # only one "channel" is considered
      assert features.shape[0] == 33*2


def test_extractor_LiSpectralFeatures():
      """ Test Li's ICPR 2016 Spectral Feature Extractor
      """

      # "pulse" in 3 color channels
      data = np.random.random((200, 3))

      extractor = LiSpectralFeatures()
      features = extractor(data)
      assert features.shape[0] == 6


def test_extractor_PPGSecure():
      """ Test PPGSecure Spectral Feature Extractor
      """
      # 5 "pulses"
      data = np.random.random((200, 5))

      extractor = PPGExtractor()
      features = extractor(data)
      # n = number of FFT coefficients (default is 32)
      # 5 (pulse signals) * (n/2 + 1)
      assert features.shape[0] == 5*17
