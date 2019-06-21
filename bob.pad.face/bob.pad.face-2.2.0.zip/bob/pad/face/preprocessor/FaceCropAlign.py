#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 30 14:11:16 2017

@author: Olegs Nikisins
"""

# ==============================================================================
# Import what is needed here:

from bob.bio.base.preprocessor import Preprocessor

import numpy as np

import bob.ip.color

import bob.ip.base

import importlib

import bob.bio.face

import logging 
logger = logging.getLogger("bob.pad.face")


# ==============================================================================
def auto_norm_image(data, annotations, n_sigma=3.0, norm_method='MAD'):
    """
    Normalizes a single channel image to range 0-255, using the data distribution
    Expects single channel images

    **method: Gaussian , MAD, MINMAX
    **n_sigma: The range which is normalized

    """

    face = data[annotations['topleft'][0]:annotations['bottomright'][0],
                 annotations['topleft'][1]:annotations['bottomright'][1]]

    face = face.astype('float')
    data = data.astype('float')

    assert(len(data.shape)==2)

    face_c = np.ma.array(face).compressed()
    # Avoiding zeros from flat field in thermal and holes in depth

    face_c=face_c[face_c>1.0]

    if norm_method=='STD':

        mu = np.mean(face_c)
        std = np.std(face_c)

        data_n=((data-mu+n_sigma*std)/(2.0*n_sigma*std))*255.0


    if norm_method=='MAD':

        med = np.median(face_c)
        mad = np.median(np.abs(face_c - med))

        data_n = ((data-med+n_sigma*mad)/(2.0*n_sigma*mad))*255.0


    if norm_method=='MINMAX':

        t_min = np.min(face_c)
        t_max = np.max(face_c)

        data_n = ((data-t_min)/(t_max-t_min))*255.0


    # Clamping to 0-255
    data_n=np.maximum(data_n,0)
    data_n=np.minimum(data_n,255)

    data_n = data_n.astype('uint8')

    return data_n

def get_mouth_center(lm):
    """
    This function returns the location of mouth center

    **Parameters:**

    ``lm`` : :py:class:`numpy.ndarray`
        A numpy array containing the coordinates of facial landmarks, (68X2)

    **Returns:**


    ``mouth_center``
        A tuple containing the location of mouth center

    """

    # Mean position of eye corners as eye centers , casted to int()

    mouth_center_t = (lm[48, :] + lm[54, :]) / 2.0

    mouth_center = (int(mouth_center_t[1]), int(mouth_center_t[0]))

    return mouth_center


# ==============================================================================
def get_eye_pos(lm):
    """
    This function returns the locations of left and right eyes

    **Parameters:**

    ``lm`` : :py:class:`numpy.ndarray`
        A numpy array containing the coordinates of facial landmarks, (68X2)

    **Returns:**

    ``reye``
        A tuple containing the location of right eye,

    ``leye``
        A tuple containing the location of left eye

    """

    # Mean position of eye corners as eye centers , casted to int()

    left_eye_t = (lm[36, :] + lm[39, :]) / 2.0
    right_eye_t = (lm[42, :] + lm[45, :]) / 2.0

    right_eye = (int(left_eye_t[1]), int(left_eye_t[0]))
    left_eye = (int(right_eye_t[1]), int(right_eye_t[0]))

    return right_eye, left_eye


def get_eye_center(lm):
    """
    This function returns the location of eye_center, midpoint of left and right eye

    **Parameters:**

    ``lm`` : :py:class:`numpy.ndarray`
        A numpy array containing the coordinates of facial landmarks, (68X2)

    **Returns:**

    ``eye_center``
        A tuple containing the location of eye_center

    """

    # Mean position of eye corners as eye centers , casted to int()

    left_eye_t = (lm[36, :] + lm[39, :]) / 2.0
    right_eye_t = (lm[42, :] + lm[45, :]) / 2.0

    eye_center = (int((left_eye_t[1]+right_eye_t[1])/2.0), int((left_eye_t[0]+right_eye_t[0])/2.0))

    return eye_center


# ==============================================================================
def detect_face_landmarks_in_image(image, method="dlib"):
    """
    This function detects a face in the input image. Two oprions for face detector , but landmark detector is always the same

    **Parameters:**

    ``image`` : 3D :py:class:`numpy.ndarray`
        A color image to detect the face in.

    ``method`` : :py:class:`str`
        A package to be used for face detection. Options supported by this
        package: "dlib" (dlib is a dependency of this package). If  bob.ip.mtcnn
        is installed in your system you can use it as-well (bob.ip.mtcnn is NOT
        a dependency of this package).

    **Returns:**

    ``annotations`` : :py:class:`dict`
        A dictionary containing annotations of the face bounding box, eye locations and facial landmarks.
        Dictionary must be as follows ``{'topleft': (row, col), 'bottomright': (row, col), 'leye': (row, col), 'reye': (row, col), 'landmarks': [(col1,row1), (col2,row2), ...]}``.
        If no annotations found an empty dictionary is returned.
        Where (rowK,colK) is the location of Kth facial landmark (K=0,...,67).
    """

    ### Face detector

    try:
        face_detection_module = importlib.import_module("bob.ip." + method)

    except ImportError:

        print("No module named bob.ip." + method +
              " trying to use default method!")

        try:
            face_detection_module = importlib.import_module("bob.ip.dlib")
            method = "dlib"
        except ImportError:
            raise ImportError("No module named bob.ip.dlib")

    if not hasattr(face_detection_module, 'FaceDetector'):
        raise AttributeError(
            "bob.ip." + method + " module has no attribute FaceDetector!")

    #### Landmark detector

    try:
        landmark_detection_module = importlib.import_module(
            "bob.ip.facelandmarks")
    except ImportError:
        raise ImportError("No module named bob.ip.facelandmarks!!")

    if not hasattr(landmark_detection_module,
                   'detect_landmarks_on_boundingbox'):
        raise AttributeError(
            "bob.ip.facelandmarksmodule has no attribute detect_landmarks_on_boundingbox!"
        )

    face_detector = face_detection_module.FaceDetector()

    data = face_detector.detect_single_face(image)

    annotations = {}

    if (data is not None) and (not all([x is None for x in data])):

        bounding_box = data[0]

        bounding_box_scaled = bounding_box.scale(0.95, True)  # is ok for dlib

        lm = landmark_detection_module.detect_landmarks_on_boundingbox(
            image, bounding_box_scaled)

        if lm is not None:

            lm = np.array(lm)

            lm = np.vstack((lm[:, 1], lm[:, 0])).T

            #print("LM",lm)

            right_eye, left_eye = get_eye_pos(lm)

            points = []

            for i in range(lm.shape[0]):

                points.append((int(lm[i, 0]), int(lm[i, 1])))

            annotations['topleft'] = bounding_box.topleft

            annotations['bottomright'] = bounding_box.bottomright

            annotations['landmarks'] = points

            annotations['leye'] = left_eye

            annotations['reye'] = right_eye

    return annotations


# ==========================================================================
def normalize_image_size_in_grayscale(image, annotations,
                                      face_size, use_face_alignment,alignment_type='default'):
    """
    This function crops the face in the input Gray-scale image given annotations
    defining the face bounding box, and eye positions.
    The size of the face is also normalized to the pre-defined dimensions.

    Two normalization options are available, which are controlled by
    ``use_face_alignment`` flag, see below.

    **Parameters:**

    ``image`` : 2D :py:class:`numpy.ndarray`
        Gray-scale input image.

    ``annotations`` : :py:class:`dict`
        A dictionary containing annotations of the face bounding box,
        eye locations and facial landmarks.
        Dictionary must be as follows: ``{'topleft': (row, col), 'bottomright': (row, col),
        'leye': (row, col), 'reye': (row, col)}``.

    ``face_size`` : :py:class:`int`
        The size of the face after normalization.

    ``use_face_alignment`` : :py:class:`bool`
        If ``False``, the re-sizing from this publication is used:
        "On the Effectiveness of Local Binary Patterns in Face Anti-spoofing"
        If ``True`` the facial image is both re-sized and aligned using
        positions of the eyes, which are given in the annotations.

    **Returns:**

    ``normbbx`` : 2D :py:class:`numpy.ndarray`
        An image of the cropped face of the size (face_size, face_size).
    """

    if use_face_alignment:


        if alignment_type=='default':

            face_eyes_norm = bob.ip.base.FaceEyesNorm(
                eyes_distance=((face_size + 1) / 2.),
                crop_size=(face_size, face_size),
                eyes_center=(face_size / 4., (face_size - 0.5) / 2.))

            right_eye, left_eye = annotations['reye'], annotations['leye']

            normalized_image = face_eyes_norm( image, right_eye = right_eye, left_eye = left_eye )

            normbbx=normalized_image.astype('uint8')

        elif alignment_type=='lightcnn': # This option overrides the facesize argument

            # This is the size of the image that this model expects

            CROPPED_IMAGE_HEIGHT = 128
            CROPPED_IMAGE_WIDTH = 128

            # eye positions for frontal images
            RIGHT_EYE_POS = (32, 44)
            LEFT_EYE_POS = (32, 84)

            EYE_CENTER_POS = (40, 64)
            MOUTH_CENTER_POS = (88, 64)


            lm=np.array(annotations['landmarks'])

            mouth_center=get_mouth_center(lm)

            eye_center=get_eye_center(lm)

            annotations['eye_center'] =eye_center

            annotations['mouth_center']=mouth_center

            light_cnn_face_cropper=bob.bio.face.preprocessor.FaceCrop(
                cropped_image_size=(CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
                cropped_positions={'eye_center': EYE_CENTER_POS, 'mouth_center': MOUTH_CENTER_POS})


            normalized_image = light_cnn_face_cropper( image, annotations=annotations)

            normbbx=normalized_image.astype('uint8')

        else:
            print('The specified alignment method {} is not implemented!'.format(alignment_type))

    else:

        cutframe = image[annotations['topleft'][0]:annotations['bottomright'][
            0], annotations['topleft'][1]:annotations['bottomright'][1]]

        tempbbx = np.ndarray((face_size, face_size), 'float64')
        normbbx = np.ndarray((face_size, face_size), 'uint8')
        bob.ip.base.scale(cutframe, tempbbx)  # normalization
        tempbbx_ = tempbbx + 0.5
        tempbbx_ = np.floor(tempbbx_)
        normbbx = np.cast['uint8'](tempbbx_)

    return normbbx


# ==========================================================================
def normalize_image_size(image, annotations, face_size,
                         rgb_output_flag, use_face_alignment,alignment_type='default'):
    """
    This function crops the face in the input image given annotations defining
    the face bounding box. The size of the face is also normalized to the
    pre-defined dimensions. For RGB inputs it is possible to return both
    color and gray-scale outputs. This option is controlled by ``rgb_output_flag``.

    Two normalization options are available, which are controlled by
    ``use_face_alignment`` flag, see below.

    **Parameters:**

    ``image`` : 2D or 3D :py:class:`numpy.ndarray`
        Input image (RGB or gray-scale).

    ``annotations`` : :py:class:`dict`
        A dictionary containing annotations of the face bounding box,
        eye locations and facial landmarks.
        Dictionary must be as follows: ``{'topleft': (row, col), 'bottomright': (row, col),
        'leye': (row, col), 'reye': (row, col)}``.

    ``face_size`` : :py:class:`int`
        The size of the face after normalization.

    ``rgb_output_flag`` : :py:class:`bool`
        Return RGB cropped face if ``True``, otherwise a gray-scale image is
        returned. Default: ``False``.

    ``use_face_alignment`` : :py:class:`bool`
        If ``False``, the facial image re-sizing from this publication is used:
        "On the Effectiveness of Local Binary Patterns in Face Anti-spoofing"
        If ``True`` the facial image is both re-sized, and aligned, using
        positions of the eyes, which are given in the annotations.

    **Returns:**

    ``face`` : 2D or 3D :py:class:`numpy.ndarray`
        An image of the cropped face of the size (face_size, face_size),
        RGB 3D or gray-scale 2D.
    """

    if len(image.shape) == 3:

        if not (rgb_output_flag):

            image = bob.ip.color.rgb_to_gray(image)

    if len(image.shape) == 2:

        image = [image]  # make gray-scale image an iterable

    result = []

    for image_channel in image:  # for all color channels in the input image

        cropped_face = normalize_image_size_in_grayscale(
            image_channel, annotations, face_size, use_face_alignment,alignment_type=alignment_type)

        result.append(cropped_face)

    face = np.stack(result, axis=0)

    face = np.squeeze(face)  # squeeze 1-st dimension for gray-scale images

    return face


# ==========================================================================
class FaceCropAlign(Preprocessor):
    """
    This function is designed to crop / size-normalize / align face
    in the input image.

    The size of the output face is ``3 x face_size x face_size`` pixels, if
    ``rgb_output_flag = True``, or ``face_size x face_size`` if
    ``rgb_output_flag = False``.

    The face can also be aligned using positions of the eyes, only when
    ``use_face_alignment = True`` and ``face_detection_method is not None``.

    Both input annotations, and automatically determined are supported.

    If ``face_detection_method is not None``, the annotations returned by
    face detector will be used in the cropping.
    Currently supported face detectors are listed in
    ``supported_face_detection_method`` argument of this class.

    If ``face_detection_method is None`` (Default), the input annotations are
    used for cropping.

    A few quality checks are supported in this function.
    The quality checks are controlled by these arguments:
    ``max_image_size``, ``min_face_size``. More details below.
    Note: ``max_image_size`` is only supported when
    ``face_detection_method is not None``.

    **Parameters:**

    ``face_size`` : :py:class:`int`
        The size of the face after normalization.

    ``rgb_output_flag`` : :py:class:`bool`
        Return RGB cropped face if ``True``, otherwise a gray-scale image is
        returned.

    ``use_face_alignment`` : :py:class:`bool`
        If set to ``True`` the face will be aligned aligned,
        using the facial landmarks detected locally.
        Works only when ``face_detection_method is not None``.

    ``alignment_type`` : :py:class:`str`
        Specifies the alignment type to use if ``use_face_alignment`` is set to ``True``
        Two methods are currently implemented:
        ``default`` which would do alignment by making eyes
        horizontally
        ``lightcnn`` which aligns the face such that eye center are mouth centers are aligned to
        predefined positions. This option overrides the face size option as the output required
        is always 128x128. This is suitable for use with LightCNN model.

    ``max_image_size`` : :py:class:`int`
        The maximum size of the image to be processed.
        ``max_image_size`` is only supported when
        ``face_detection_method is not None``.
        Default: ``None``.

    ``face_detection_method`` : :py:class:`str`
        A package to be used for face detection and landmark detection.
        Options supported by this class:
        "dlib" and "mtcnn", which are listed in
        ``self.supported_face_detection_method`` argument.
        Default: ``None``.

    ``min_face_size`` : :py:class:`int`
        The minimal size of the face in pixels to be processed.
        Default: None.

    ``normalization_function`` : function
        Function to be applied to the input image before cropping and
        normalization. For  example, type-casting to uint8 format and
        data normalization, using facial region only (annotations).
        The expected signature of the function:
        ``normalization_function(image, annotations, **kwargs)``.

    ``normalization_function_kwargs`` : :py:class:`dict`
        Key-word arguments for the ``normalization_function``.
    """

    # ==========================================================================
    def __init__(self, face_size,
                 rgb_output_flag,
                 use_face_alignment,
                 alignment_type='default',
                 max_image_size=None,
                 face_detection_method=None,
                 min_face_size=None,
                 normalization_function=None,
                 normalization_function_kwargs = None):

        Preprocessor.__init__(self, face_size=face_size,
                              rgb_output_flag=rgb_output_flag,
                              use_face_alignment=use_face_alignment,
                              alignment_type=alignment_type,
                              max_image_size=max_image_size,
                              face_detection_method=face_detection_method,
                              min_face_size=min_face_size,
                              normalization_function=normalization_function,
                              normalization_function_kwargs = normalization_function_kwargs)

        self.face_size = face_size
        self.rgb_output_flag = rgb_output_flag
        self.use_face_alignment = use_face_alignment
        self.alignment_type=alignment_type

        self.max_image_size = max_image_size
        self.face_detection_method = face_detection_method
        self.min_face_size = min_face_size
        self.normalization_function = normalization_function
        self.normalization_function_kwargs = normalization_function_kwargs


        self.supported_face_detection_method = ["dlib", "mtcnn"]


        self.supported_alignment_method = ["default", "lightcnn"]

        if use_face_alignment:

            if self.alignment_type not in self.supported_alignment_method:

                raise ValueError('The alignment type {} is not supported'.format(self.alignment_type))



        if self.face_detection_method is not None:

            if self.face_detection_method not in self.supported_face_detection_method:

                raise ValueError('The {0} face detection method is not supported by this class. '
                    'Currently supported face detectors are: bob.ip.{1}, bob.ip.{2}'.
                    format(face_detection_method, self.supported_face_detection_method[0], self.supported_face_detection_method[1]))

    # ==========================================================================
    def __call__(self, image, annotations=None):
        """
        This function is designed to crop / size-normalize / align face
        in the input image.

        The size of the output face is ``3 x face_size x face_size`` pixels, if
        ``rgb_output_flag = True``, or ``face_size x face_size`` if
        ``rgb_output_flag = False``.

        The face can also be aligned using positions of the eyes, only when
        ``use_face_alignment = True`` and ``face_detection_method is not None``.

        Both input annotations, and automatically determined are supported.

        If ``face_detection_method is not None``, the annotations returned by
        face detector will be used in the cropping.
        Currently supported face detectors are listed in
        ``supported_face_detection_method`` argument of this class.

        If ``face_detection_method is None`` (Default), the input annotations are
        used for cropping.

        A few quality checks are supported in this function.
        The quality checks are controlled by these arguments:
        ``max_image_size``, ``min_face_size``. More details below.
        Note: ``max_image_size`` is only supported when
        ``face_detection_method is not None``.

        **Parameters:**

        ``image`` : 2D or 3D :py:class:`numpy.ndarray`
            Input image (RGB or gray-scale) or None.

        ``annotations`` : :py:class:`dict` or None
            A dictionary containing annotations of the face bounding box.
            Dictionary must be as follows:
            ``{'topleft': (row, col), 'bottomright': (row, col)}``
            Default: None .

        **Returns:**

        ``norm_face_image`` : 2D or 3D :py:class:`numpy.ndarray` or None
            An image of the cropped / aligned face, of the size:
            (self.face_size, self.face_size), RGB 3D or gray-scale 2D.
        """

        # sanity check:
        if not self.rgb_output_flag and len(image.shape) != 2:
          logger.warning("This image has 3 channels")
          if self.normalization_function is not None:
            import bob.ip.color
            image = bob.ip.color.rgb_to_gray(image)
            logger.warning("Image has been converted to grayscale")


        if self.face_detection_method is not None:

            if self.max_image_size is not None: # max_image_size = 1920, for example

                if np.max(image.shape) > self.max_image_size: # quality check

                    return None

            try:

                annotations = detect_face_landmarks_in_image(image=image,
                    method=self.face_detection_method)

            except:
                logger.warning("Face not detected")
                return None

            if not annotations:  # if empty dictionary is returned

                return None

        if annotations is None:  # annotations are missing for this image

            return None

        if self.min_face_size is not None: # quality check

            # size of the face
            original_face_size = np.min(
                np.array(annotations['bottomright']) -
                np.array(annotations['topleft']))

            if original_face_size < self.min_face_size:  # check if face size is above the threshold

                return None

        if self.normalization_function is not None:
            image = self.normalization_function(image, annotations, **self.normalization_function_kwargs)

        norm_face_image = normalize_image_size(image=image,
                                               annotations=annotations,
                                               face_size=self.face_size,
                                               rgb_output_flag=self.rgb_output_flag,
                                               use_face_alignment=self.use_face_alignment,
                                               alignment_type=self.alignment_type)

        return norm_face_image
