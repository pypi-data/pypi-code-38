#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 10:13:21 2017

@author: Olegs Nikisins
"""

#==============================================================================
# Import what is needed here:

from bob.bio.base.extractor import Extractor

import numpy as np

import sys

import bob.bio.video

#==============================================================================
# Main body:


class FrameDiffFeatures(Extractor):
    """
    This class is designed to extract features describing frame differences.

    The class allows to compute the following features in the window of the
    length defined by ``window_size`` argument:

        1. The minimum value observed on the cluster
        2. The maximum value observed on the cluster
        3. The mean value observed
        4. The standard deviation on the cluster (unbiased estimator)
        5. The DC ratio (D) as defined by:

    .. math::

        D(N) = (\sum_{i=1}^N{|FFT_i|}) / (|FFT_0|)

    **Parameters:**

    ``window_size`` : :py:class:`int`
        The size of the window to use for feature computation.

    ``overlap`` : :py:class:`int`
        Determines the window overlapping; this number has to be between
        0 (no overlapping) and 'window-size'-1. Default: 0.
    """

    def __init__(self, window_size, overlap=0):

        Extractor.__init__(self, window_size=window_size, overlap=overlap)

        self.window_size = window_size
        self.overlap = overlap

    #==========================================================================
    def dcratio(self, arr):
        """
        Calculates the DC ratio as defined by the following formula:

        .. math::

            D(N) = (\sum_{i=1}^N{|FFT_i|}) / (|FFT_0|)

        **Parameters:**

        ``arr`` : 1D :py:class:`numpy.ndarray`
            A 1D array containg frame differences.

        **Returns:**

        ``dcratio`` : :py:class:`float`
            Calculated DC ratio.
        """

        if arr.shape[0] <= 1:
            return 0.

        res = np.fft.fft(arr.astype('complex128'))
        res = np.absolute(res)  # absolute value

        if res[0] == 0:
            s = sum(res[1:])
            if s > 0:
                return sys.float_info.max
            elif s < 0:
                return -sys.float_info.max
            else:
                return 0

        dcratio = sum(res[1:]) / res[0]

        return dcratio

    #==========================================================================
    def remove_nan_rows(self, data):
        """
        This function removes rows of nan's from the input array. If the input
        array contains nan's only, then an array of ones of the size
        (1 x n_features) is returned.

        **Parameters:**

        ``data`` : 2D :py:class:`numpy.ndarray`
            An input array of features. Rows - samples, columns - features.

        **Returns:**

        ``ret_arr`` : 2D :py:class:`numpy.ndarray`
           Array of features without nan samples. Rows - samples, columns - features.
        """

        d = np.vstack(data)

        ret_arr = d[~np.isnan(d.sum(axis=1)), :]

        if ret_arr.shape[0] == 0:  # if array is empty, return array of ones

            ret_arr = np.ones((1, ret_arr.shape[1]))

        return ret_arr

    #==========================================================================
    def cluster_5quantities(self, arr, window_size, overlap):
        """
        Calculates the clustered values as described at the paper: Counter-
        Measures to Photo Attacks in Face Recognition: a public database and a
        baseline, Anjos & Marcel, IJCB'11.

        This script will output a number of clustered observations containing the 5
        described quantities for windows of a configurable size (N):

            1. The minimum value observed on the cluster
            2. The maximum value observed on the cluster
            3. The mean value observed
            4. The standard deviation on the cluster (unbiased estimator)
            5. The DC ratio (D) as defined by:

        .. math::

            D(N) = (\sum_{i=1}^N{|FFT_i|}) / (|FFT_0|)

        .. note::

            We always ignore the first entry from the input array as, by
            definition, it is always zero.

        **Parameters:**

        ``arr`` : 1D :py:class:`numpy.ndarray`
            A 1D array containg frame differences.

        ``window_size`` : :py:class:`int`
            The size of the window to use for feature computation.

        ``overlap`` : :py:class:`int`
            Determines the window overlapping; this number has to be between
            0 (no overlapping) and 'window-size'-1.

        **Returns:**

        ``retval`` : 2D :py:class:`numpy.ndarray`
            Array of features without nan samples. Rows - samples, columns - features.
            Here sample corresponds to features computed from the particular
            window of the length ``window_size``.
        """

        retval = np.ndarray((arr.shape[0], 5), dtype='float64')
        retval[:] = np.NaN

        for k in range(0, arr.shape[0] - window_size + 1,
                       window_size - overlap):

            obs = arr[k:k + window_size].copy()

            # replace NaN values by set mean so they don't disturb calculations
            # much
            ok = obs[~np.isnan(obs)]

            obs[np.isnan(obs)] = ok.mean()

            retval[k + window_size - 1] = \
                (obs.min(), obs.max(), obs.mean(), obs.std(ddof=1), self.dcratio(obs))

        retval = self.remove_nan_rows(retval)  # clean-up nan's in the array

        return retval

    #==========================================================================
    def convert_arr_to_frame_cont(self, data):
        """
        This function converts an array of samples into a FrameContainer, where
        each frame stores features of a particular sample.

        **Parameters:**

        ``data`` : 2D :py:class:`numpy.ndarray`
            An input array of features of the size
            (Nr. of samples X Nr. of features).

        **Returns:**

        ``frames`` : FrameContainer
            Resulting FrameContainer, where each frame stores features of
            a particular sample.
        """

        frames = bob.bio.video.FrameContainer(
        )  # initialize the FrameContainer

        for idx, sample in enumerate(data):

            frames.add(idx, sample)

        return frames

    #==========================================================================
    def comp_features(self, data, window_size, overlap):
        """
        This function computes features for frame differences in the facial and
        non-facial regions.

        **Parameters:**

        ``data`` : 2D :py:class:`numpy.ndarray`
            An input array of frame differences in facial and non-facial regions.
            The first column contains frame differences of facial regions.
            The second column contains frame differences of non-facial/background regions.

        ``window_size`` : :py:class:`int`
            The size of the window to use for feature computation.

        ``overlap`` : :py:class:`int`
            Determines the window overlapping; this number has to be between
            0 (no overlapping) and 'window-size'-1. Default: 0.

        **Returns:**

        ``frames`` : FrameContainer
            Features describing frame differences, stored in the FrameContainer.
        """

        d_face = self.cluster_5quantities(data[:, 0], window_size, overlap)

        d_bg = self.cluster_5quantities(data[:, 1], window_size, overlap)

        min_len = min(len(d_face), len(d_bg))

        features = np.hstack((d_face[:min_len], d_bg[:min_len]))

        frames = self.convert_arr_to_frame_cont(features)

        return frames

    #==========================================================================
    def __call__(self, data):
        """
        This function computes features for frame differences in the facial and
        non-facial regions.

        **Parameters:**

        ``data`` : 2D :py:class:`numpy.ndarray`
            An input array of frame differences in facial and non-facial regions.
            The first column contains frame differences of facial regions.
            The second column contains frame differences of non-facial/background regions.

        **Returns:**

        ``frames`` : FrameContainer
            Features describing frame differences, stored in the FrameContainer.
        """

        frames = self.comp_features(data, self.window_size, self.overlap)

        return frames

    #==========================================================================
    def write_feature(self, frames, file_name):
        """
        Writes the given data (that has been generated using the __call__ function of this class) to file.
        This method overwrites the write_data() method of the Extractor class.

        **Parameters:**

        ``frames`` :
            Data returned by the __call__ method of the class.

        ``file_name`` : :py:class:`str`
            Name of the file.
        """

        bob.bio.video.extractor.Wrapper(Extractor()).write_feature(
            frames, file_name)

    #==========================================================================
    def read_feature(self, file_name):
        """
        Reads the preprocessed data from file.
        This method overwrites the read_data() method of the Extractor class.

        **Parameters:**

        ``file_name`` : :py:class:`str`
            Name of the file.

        **Returns:**

        ``frames`` : :py:class:`bob.bio.video.FrameContainer`
            Frames stored in the frame container.
        """

        frames = bob.bio.video.extractor.Wrapper(
            Extractor()).read_feature(file_name)

        return frames
