#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 14:14:23 2017

@author: Olegs Nikisins
"""

#==============================================================================
# Import what is needed here:

from bob.bio.base.preprocessor import Preprocessor

import numpy as np

import bob.bio.video

import bob.ip.base

import bob.ip.color

import bob.ip.facedetect

import logging

#==============================================================================
# Main body:

logger = logging.getLogger(__name__)


class FrameDifference(Preprocessor):
    """
    This class is designed to compute frame differences for both facial and
    background regions. The constraint of minimal size of the face can be
    applied to input video selecting only the frames overcoming the threshold.
    This behavior is controlled by ``check_face_size_flag`` and ``min_face_size``
    arguments of the class.
    It is also possible to compute the frame differences for a limited number
    of frames specifying the ``number_of_frames`` parameter.

    **Parameters:**

    ``number_of_frames`` : :py:class:`int`
        The number of frames to extract the frame differences from.
        If ``None``, all frames of the input video are used. Default: ``None``.

    ``min_face_size`` : :py:class:`int`
        The minimal size of the face in pixels. Only valid when ``check_face_size_flag``
        is set to True. Default: 50.
    """

    def __init__(self,
                 number_of_frames=None,
                 min_face_size=50,
                 **kwargs):

        super(FrameDifference, self).__init__(
            number_of_frames=number_of_frames,
            min_face_size=min_face_size,
            **kwargs)

        self.number_of_frames = number_of_frames
        self.min_face_size = min_face_size

    #==========================================================================
    def eval_face_differences(self, previous, current, annotations):
        """
        Evaluates the normalized frame difference on the face region.

        If bounding_box is None or invalid, returns 0.

        **Parameters:**

        ``previous`` : 2D :py:class:`numpy.ndarray`
            Previous frame as a gray-scaled image

        ``current`` : 2D :py:class:`numpy.ndarray`
            The current frame as a gray-scaled image

        ``annotations`` : :py:class:`dict`
            A dictionary containing annotations of the face bounding box.
            Dictionary must be as follows ``{'topleft': (row, col), 'bottomright': (row, col)}``.

        **Returns:**

        ``face`` : :py:class:`float`
            A size normalized integral difference of facial regions in two input
            images.
        """

        prev = previous[annotations['topleft'][0]:annotations['bottomright'][
            0], annotations['topleft'][1]:annotations['bottomright'][1]]

        curr = current[annotations['topleft'][0]:annotations['bottomright'][0],
                       annotations['topleft'][1]:annotations['bottomright'][1]]

        face_diff = abs(curr.astype('int32') - prev.astype('int32'))

        face = face_diff.sum()

        face /= float(face_diff.size)

        return face

    #==========================================================================
    def eval_background_differences(self,
                                    previous,
                                    current,
                                    annotations,
                                    border=None):
        """
        Evaluates the normalized frame difference on the background.

        If bounding_box is None or invalid, returns 0.

        **Parameters:**

        ``previous`` : 2D :py:class:`numpy.ndarray`
            Previous frame as a gray-scaled image

        ``current`` : 2D :py:class:`numpy.ndarray`
            The current frame as a gray-scaled image

        ``annotations`` : :py:class:`dict`
            A dictionary containing annotations of the face bounding box.
            Dictionary must be as follows ``{'topleft': (row, col), 'bottomright': (row, col)}``.

        ``border`` : :py:class:`int`
            The border size to consider. If set to ``None``, consider all image from the
            face location up to the end. Default: ``None``.

        **Returns:**

        ``bg`` : :py:class:`float`
            A size normalized integral difference of non-facial regions in two input
            images.
        """

        height = annotations['bottomright'][0] - annotations['topleft'][0]
        width = annotations['bottomright'][1] - annotations['topleft'][1]

        full_diff = abs(current.astype('int32') - previous.astype('int32'))

        if border is None:
            full = full_diff.sum()
            full_size = full_diff.size

        else:

            y1 = annotations['topleft'][0] - border
            if y1 < 0:
                y1 = 0
            x1 = annotations['topleft'][1] - border
            if x1 < 0:
                x1 = 0
            y2 = y1 + height + (2 * border)
            if y2 > full_diff.shape[0]:
                y2 = full_diff.shape[0]
            x2 = x1 + width + (2 * border)
            if x2 > full_diff.shape[1]:
                x2 = full_diff.shape[1]
            full = full_diff[y1:y2, x1:x2].sum()
            full_size = full_diff[y1:y2, x1:x2].size

        face_diff = full_diff[annotations['topleft'][0]:(
            annotations['topleft'][0] + height), annotations['topleft'][1]:(
                annotations['topleft'][1] + width)]

        # calculates the differences in the face and background areas
        face = face_diff.sum()
        bg = full - face

        normalization = float(full_size - face_diff.size)
        if normalization < 1:  # prevents zero division
            bg = 0.0
        else:
            bg /= float(full_size - face_diff.size)

        return bg

    #==========================================================================
    def check_face_size(self, frame_container, annotations, min_face_size):
        """
        Return the FrameContainer containing the frames with faces of the
        size overcoming the specified threshold. The annotations for the selected
        frames are also returned.

        **Parameters:**

        ``frame_container`` : FrameContainer
            Video data stored in the FrameContainer, see ``bob.bio.video.utils.FrameContainer``
            for further details.

        ``annotations`` : :py:class:`dict`
            A dictionary containing the annotations for each frame in the video.
            Dictionary structure: ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.
            Where ``frameN_dict = {'topleft': (row, col), 'bottomright': (row, col)}``
            is the dictionary defining the coordinates of the face bounding box in frame N.

        ``min_face_size`` : :py:class:`int`
            The minimal size of the face in pixels.

        **Returns:**

        ``selected_frames`` : FrameContainer
            Selected frames stored in the FrameContainer.

        ``selected_annotations`` : :py:class:`dict`
            A dictionary containing the annotations for selected frames.
            Dictionary structure: ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.
            Where ``frameN_dict = {'topleft': (row, col), 'bottomright': (row, col)}``
            is the dictionary defining the coordinates of the face bounding box in frame N.
        """

        selected_frames = bob.bio.video.FrameContainer(
        )  # initialize the FrameContainer

        selected_annotations = {}

        selected_frame_idx = 0

        for idx in range(0, len(annotations)):  # idx - frame index

            # annotations for particular frame
            frame_annotations = annotations[str(idx)]

            if not frame_annotations:
                continue

            # Estimate bottomright and topleft if they are not available:
            if 'topleft' not in frame_annotations:
                bbx = bob.ip.facedetect.bounding_box_from_annotation(
                    **frame_annotations)
                frame_annotations['topleft'] = bbx.topleft
                frame_annotations['bottomright'] = bbx.bottomright

            # size of current face
            face_size = np.min(
                np.array(frame_annotations['bottomright']) -
                np.array(frame_annotations['topleft']))

            if face_size >= min_face_size:  # check if face size is above the threshold

                selected_frame = frame_container[idx][1]  # get current frame

                selected_frames.add(
                    selected_frame_idx,
                    selected_frame)  # add current frame to FrameContainer

                selected_annotations[str(selected_frame_idx)] = annotations[
                    str(idx)]

                selected_frame_idx = selected_frame_idx + 1

        return selected_frames, selected_annotations

    #==========================================================================
    def comp_face_bg_diff(self, frames, annotations, number_of_frames=None):
        """
        This function computes the frame differences for both facial and background
        regions. These parameters are computed for ``number_of_frames`` frames
        in the input FrameContainer.

        **Parameters:**

        ``frames`` : FrameContainer
            RGB video data stored in the FrameContainer, see ``bob.bio.video.utils.FrameContainer``
            for further details.

        ``annotations`` : :py:class:`dict`
            A dictionary containing the annotations for each frame in the video.
            Dictionary structure: ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.
            Where ``frameN_dict = {'topleft': (row, col), 'bottomright': (row, col)}``
            is the dictionary defining the coordinates of the face bounding box in frame N.

        ``number_of_frames`` : :py:class:`int`
            The number of frames to use in processing. If ``None``, all frames of the
            input video are used. Default: ``None``.

        **Returns:**

        ``diff`` : 2D :py:class:`numpy.ndarray`
            An array of the size ``(number_of_frames - 1) x 2``.
            The first column contains frame differences of facial regions.
            The second column contains frame differences of non-facial/background regions.
        """

        # Compute the number of frames to process:
        if number_of_frames is not None:
            number_of_frames = np.min([len(frames), number_of_frames])
        else:
            number_of_frames = len(frames)

        previous = frames[0][1]  # the first frame in the video

        if len(previous.shape) == 3:  # if RGB convert to gray-scale
            previous = bob.ip.color.rgb_to_gray(previous)

        diff = []

        for k in range(1, number_of_frames):

            current = frames[k][1]

            if len(current.shape) == 3:  # if RGB convert to gray-scale
                current = bob.ip.color.rgb_to_gray(current)

            face_diff = self.eval_face_differences(previous, current,
                                                   annotations[str(k)])
            bg_diff = self.eval_background_differences(
                previous, current, annotations[str(k)], None)

            diff.append((face_diff, bg_diff))

            # swap buffers: current <=> previous
            tmp = previous
            previous = current
            current = tmp

        if not diff:  # if list is empty

            diff = [(np.NaN, np.NaN)]

        diff = np.vstack(diff)

        return diff

    #==========================================================================
    def select_annotated_frames(self, frames, annotations):
        """
        Select only annotated frames in the input FrameContainer ``frames``.

        **Parameters:**

        ``frames`` : FrameContainer
            Video data stored in the FrameContainer, see ``bob.bio.video.utils.FrameContainer``
            for further details.

        ``annotations`` : :py:class:`dict`
            A dictionary containing the annotations for each frame in the video.
            Dictionary structure: ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.
            Where ``frameN_dict = {'topleft': (row, col), 'bottomright': (row, col)}``
            is the dictionary defining the coordinates of the face bounding box in frame N.

        **Returns:**

        ``cleaned_frame_container`` : FrameContainer
            FrameContainer containing the annotated frames only.

        ``cleaned_annotations`` : :py:class:`dict`
            A dictionary containing the annotations for each frame in the output video.
            Dictionary structure: ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.
            Where ``frameN_dict = {'topleft': (row, col), 'bottomright': (row, col)}``
            is the dictionary defining the coordinates of the face bounding box in frame N.
        """

        annotated_frames = np.sort([
            np.int(item) for item in annotations.keys()
        ])  # annotated frame numbers

        available_frames = range(
            0, len(frames))  # frame numbers in the input video

        valid_frames = list(
            set(annotated_frames).intersection(
                available_frames))  # valid and annotated frames

        cleaned_frame_container = bob.bio.video.FrameContainer(
        )  # initialize the FrameContainer

        cleaned_annotations = {}

        for idx, valid_frame_num in enumerate(valid_frames):
            # valid_frame_num - is the number of the original frame having annotations

            cleaned_annotations[str(idx)] = annotations[str(
                valid_frame_num)]  # correct the frame numbers

            selected_frame = frames[valid_frame_num][1]  # get current frame

            cleaned_frame_container.add(
                idx, selected_frame)  # add current frame to FrameContainer

        return cleaned_frame_container, cleaned_annotations

    #==========================================================================
    def __call__(self, frames, annotations):
        """
        This method calls the ``comp_face_bg_diff`` function of this class
        computing the frame differences for both facial and background regions.
        The frame differences are computed for selected frames, which are returned
        by ``check_face_size`` function of this class.

        **Parameters:**

        ``frames`` : FrameContainer
            RGB video data stored in the FrameContainer, see ``bob.bio.video.utils.FrameContainer``
            for further details.

        ``annotations`` : :py:class:`dict`
            A dictionary containing the annotations for each frame in the video.
            Dictionary structure: ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.
            Where ``frameN_dict = {'topleft': (row, col), 'bottomright': (row, col)}``
            is the dictionary defining the coordinates of the face bounding box in frame N.

        **Returns:**

        ``diff`` : 2D :py:class:`numpy.ndarray`
            An array of the size ``(number_of_frames - 1) x 2``.
            The first column contains frame differences of facial regions.
            The second column contains frame differences of non-facial/background regions.
        """

        if len(frames) != len(annotations):  # if some annotations are missing

            # Select only annotated frames:
            frames, annotations = self.select_annotated_frames(
                frames, annotations)

        selected_frames, selected_annotations = self.check_face_size(
            frames, annotations, self.min_face_size)

        if not len(selected_annotations):
            logger.warn("None of the annotations are valid.")
            return None

        diff = self.comp_face_bg_diff(
            frames=selected_frames,
            annotations=selected_annotations,
            number_of_frames=self.number_of_frames)

        return diff
