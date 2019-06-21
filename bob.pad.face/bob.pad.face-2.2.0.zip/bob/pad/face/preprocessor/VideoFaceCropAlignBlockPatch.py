#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 15:38:28 2018

@author: Olegs Nikisins
"""

# =============================================================================
# Import what is needed here:

from bob.bio.base.preprocessor import Preprocessor

import bob.bio.video

import numpy as np

from bob.bio.video.utils import FrameSelector

from bob.bio.video.preprocessor import Wrapper

import bob.ip.dlib

import cv2

from skimage import morphology

from bob.bio.video.utils.FrameContainer import FrameContainer


# =============================================================================
def get_face_contour_mask(image, filt_size = None, erode_flag = False, crop_flag = False):
    """
    This function computes the binary mask for the facial region using
    landmarks of the face contour. The following steps are executed:

    1. Facial landmarks are detected in the input facial image.
    2. Binary mask of the face region is computed using landmarks
    corresponding to face contour.
    3. Mask can next be cropped, like if it was filtered with a filter
       of the size ``(filt_size x filt_size)``.
    4. Binary erosion can also be applied to the mask. The disk structuring
       element is used for dilation.
       The diameter of the disk is ``filt_size``.

    **Parameters:**

    ``image`` : 2D to ND :py:class:`numpy.ndarray`
        Input image (gray-scale, RGB or multi-spectral).
        The expected dimensionality of the image is:
        ``num_channels x w x h``.

    ``filt_size`` : int
        If given, a binary mask can be cropped like if it was fileter
        with a filter of size ``(filt_size x filt_size)``.
        Also, the mask can be eroded with disk of the size ``filt_size``.

    ``erode_flag`` : bool
        If set to ``True``, a binary mask will be eroded with a disk
        structuring element of the diameter ``filt_size``.

    ``crop_flag`` : bool
        If set to ``True``, a binary mask will be cropped like if it
        was fileter with a filter of size ``(filt_size x filt_size)``.

    **Returns:**

    ``mask`` : 2D :py:class:`numpy.ndarray`
        A binary maks of the face region.
    """

    # landmarks
    detector = bob.ip.dlib.DlibLandmarkExtraction()
    points = detector(image)

#    mask_rgb = 1-np.transpose(np.any(image==255, axis=0)).astype(np.int)

    if points is not None:

        temp_mask = np.zeros((image.shape[-2], image.shape[-1]))

        # face_contour = points[0:27]  # this is a complete contour
        # face_contour = points[:16]  # this is a lower half-face
        face_contour = points[:16]  # this is a lower half-face
        # go vertical from to the top of image from lower half of the face:
        face_contour = [(0, face_contour[0][1])] + face_contour + [(0, face_contour[-1][1])]

        hull = cv2.convexHull(np.array(face_contour))

        mask = cv2.drawContours(temp_mask, [hull], 0, 1, -1)

#        mask = mask*mask_rgb

    else:

        mask = np.ones((image.shape[-2], image.shape[-1]))

#        mask = mask*mask_rgb

    if filt_size is not None and erode_flag:

        selem = morphology.disk(filt_size)
        # invert and dilate the mask to obtain erosion without black border:
        mask = morphology.binary_dilation(1-mask, selem=selem)
        # invert the mask back
        mask = 1-mask

    if filt_size is not None and crop_flag:

        start = np.int(np.floor(filt_size/2.))
        end = np.int(np.ceil(filt_size/2.))

        mask = mask[start:mask.shape[0]-end+1, start:mask.shape[1]-end+1]

    return mask


class VideoFaceCropAlignBlockPatch(Preprocessor, object):
    """
    This class is designed to first detect, crop and align face in all input
    channels, and then to extract patches from the ROI in the cropped faces.

    The computation flow is the following:

    1. Detect, crop and align facial region in all input channels.
    2. Concatenate all channels forming a single multi-channel video data.
    3. Extract multi-channel patches from the ROI of the multi-channel video data.
    4. Vectorize extracted patches.

    **Parameters:**

    ``preprocessors`` : :py:class:`dict`
        A dictionary containing preprocessors for all channels. Dictionary
        structure is the following:
        ``{channel_name_1: bob.bio.video.preprocessor.Wrapper, ``
        ``channel_name_2: bob.bio.video.preprocessor.Wrapper, ...}``
        Note: video, not image, preprocessors are expected.

    ``channel_names`` : [str]
        A list of chanenl names. Channels will be processed in this order.

    ``return_multi_channel_flag`` : bool
        If this flag is set to ``True``, a multi-channel video data will be
        returned. Otherwise, patches extracted from ROI of the video are
        returned.
        Default: ``False``.

    ``block_patch_preprocessor`` : object
        An instance of the ``bob.pad.face.preprocessor.BlockPatch`` class,
        which is used to extract multi-spectral patches from ROI of the facial
        region.

    ``get_face_contour_mask_dict`` : dict or None
        Kwargs for the ``get_face_contour_mask()`` function. See description
        of this function for more details. If not ``None``, a binary mask of
        the face will be computed. Patches outside of the mask are set to zero.
        Default: None

    ``append_mask_flag`` : bool
        If set to ``True``, mask will be flattened and concatenated to output
        array of patches. NOTE: mame sure extractor is capable of handling this
        case in case you set this flag to ``True``.
        Default: ``False``

    ``feature_extractor`` : object
        An instance of the feature extractor to be applied to the patches.
        Default is ``None``, meaning that **patches** are returned by the
        preprocessor, and no feature extraction is applied.
        Defining ``feature_extractor`` instance can be usefull, for example,
        when saving the pathes is taking too much memory.
        Note, that ``feature_extractor`` should be able to process
        FrameContainers.
        Default: ``None``
    """

    # =========================================================================
    def __init__(self, preprocessors,
                 channel_names,
                 return_multi_channel_flag = False,
                 block_patch_preprocessor = None,
                 get_face_contour_mask_dict = None,
                 append_mask_flag = False,
                 feature_extractor = None):

        super(VideoFaceCropAlignBlockPatch, self).__init__(preprocessors = preprocessors,
                                                           channel_names = channel_names,
                                                           return_multi_channel_flag = return_multi_channel_flag,
                                                           block_patch_preprocessor = block_patch_preprocessor,
                                                           get_face_contour_mask_dict = get_face_contour_mask_dict,
                                                           append_mask_flag = append_mask_flag,
                                                           feature_extractor = feature_extractor)

        self.preprocessors = preprocessors

        self.channel_names = channel_names

        self.return_multi_channel_flag = return_multi_channel_flag

        self.block_patch_preprocessor = block_patch_preprocessor

        self.get_face_contour_mask_dict = get_face_contour_mask_dict

        self.append_mask_flag = append_mask_flag

        self.feature_extractor = feature_extractor


    # =========================================================================
    def __call__(self, frames, annotations):
        """
        This function is designed to first detect, crop and align face in all
        input channels, and then to extract patches from the ROI in the
        cropped faces.

        The computation flow is the following:
        1. Detect, crop and align facial region in all input channels.
        2. Concatenate all channels forming a single multi-channel video data.
        3. Extract multi-channel patches from the ROI of the multi-channel video
           data.
        4. Vectorize extracted patches.
        5. If ``feature_extractor`` is defined, the extractor will be applied
           to the patches. By default, no extractor is applied.

        **Parameters:**

        ``frames`` : :py:class:`dict`
            A dictionary containing FrameContainers for multiple channels.

        ``annotations`` : :py:class:`dict`
            A dictionary containing annotations for
            each frame in the video.
            Dictionary structure (non-SWIR channels):
            ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.
            Where
            ``frameN_dict`` contains coordinates of the
            face bounding box and landmarks in frame N.

            Also, ``annotations`` dictionary is expected to have a key namely
            ``face_roi``. This key point to annotations defining ROI in the
            facial region. ROI is annotated as follows:
            ``annotations['face_roi'][0] = [x_top_left, y_top_left]``
            ``annotations['face_roi'][1] = [x_bottom_right, y_bottom_right]``
            If ``face_roi`` annotations are undefined, the patches will be
            extracted from an entire cropped facial image.

        **Returns:**

        FrameContainer
            Contains either multi-channel preprocessed data, or patches
            extracted from this data. The output is controlled by
            ``return_multi_channel_flag`` of this class.
        """

        # If an input is a FrameContainer convert it to the dictionary with the key from the self.channel_names:
        if isinstance(frames, FrameContainer):
            frames = dict(zip(self.channel_names, [frames]))

        # Preprocess all channels:
        preprocessed = [self.preprocessors[channel](frames[channel], annotations) for channel in self.channel_names]

        if None in preprocessed:

            return None

        # convert all channels to arrays:
        preprocessed_arrays = [item.as_array() for item in preprocessed]

        # Convert arrays of dimensionality 3 to 4 if necessary:
        preprocessed_arrays = [np.expand_dims(item, axis=1) if len(item.shape)==3 else item for item in preprocessed_arrays]

        # Concatenate streams channel-wise:
        preprocessed_arrays = np.concatenate(preprocessed_arrays, axis=1)

        # Convert to frame container:
        preprocessed_fc = bob.bio.video.FrameContainer()  # initialize the FrameContainer
        [preprocessed_fc.add(idx, item) for idx, item in enumerate(preprocessed_arrays)]

        if self.return_multi_channel_flag:

            return preprocessed_fc

        if self.block_patch_preprocessor is not None:

            frame_selector = FrameSelector(selection_style = "all")

            video_block_patch = Wrapper(preprocessor = self.block_patch_preprocessor,
                                        frame_selector = frame_selector)
        else:
            return None

        if 'face_roi' in annotations: # if ROI annotations are given

            roi_annotations={}

            roi_annotations['0'] = annotations['face_roi']

        else: # extract patches from the whole image

            roi_annotations = None

        patches = video_block_patch(frames = preprocessed_fc, annotations = roi_annotations)

        # compute face masks if needed:
        if self.get_face_contour_mask_dict is not None:

            patches_masked = bob.bio.video.FrameContainer()  # initialize the FrameContainer

            for idx, (frame, frame_patches) in enumerate(zip(preprocessed_arrays, patches)):

                # here we assume that first three slices 0:3 correspond to RGB image:
                mask = get_face_contour_mask(image = frame[0:3, :, :], **self.get_face_contour_mask_dict)

                if mask is not None:

                    mask = mask.flatten()

                    if self.append_mask_flag:

                        patches_masked.add(idx, np.c_[frame_patches[1], mask])

                    else:

                        patches_masked.add(idx, np.transpose(np.transpose(frame_patches[1])*mask))

            patches = patches_masked

        # Features can be extracted in the preprocessing stage, if feature extractor is given.
        # For example, this can be used, when memory needed for saving the patches is too big.
        if self.feature_extractor is not None:

            features = self.feature_extractor(patches)

            return features

        return patches


    # =========================================================================
    def write_data(self, frames, file_name):
        """
        Writes the given data (that has been generated using the __call__
        function of this class) to file. This method overwrites the write_data()
        method of the Preprocessor class.

        **Parameters:**

        ``frames`` :
            data returned by the __call__ method of the class.

        ``file_name`` : :py:class:`str`
            name of the file.
        """

        self.preprocessors[self.channel_names[0]].write_data(frames, file_name)


    # =========================================================================
    def read_data(self, file_name):
        """
        Reads the preprocessed data from file.
        This method overwrites the read_data() method of the Preprocessor class.

        **Parameters:**

        ``file_name`` : :py:class:`str`
            name of the file.

        **Returns:**

        ``frames`` : :py:class:`bob.bio.video.FrameContainer`
            Frames stored in the frame container.
        """

        frames = self.preprocessors[self.channel_names[0]].read_data(file_name)

        return frames


