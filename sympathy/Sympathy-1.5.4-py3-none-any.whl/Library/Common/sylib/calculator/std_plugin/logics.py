# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import print_function, division, unicode_literals
import inspect
from six.moves import zip as izip

import numpy as np


def find_sequences_indices(mask):
    """
    Return iterator with tuples of start and end indices for all sequences
    of True values in mask.

    Parameters
    ----------
    mask : np.ndarray
        The mask the function should be performed on.

    Returns
    -------
    tuples
        Iterator with a tuple of start and end indices for each sequences of
        True values in the input.

     Examples
    --------
    >>> mask = np.array([False, True, True, False])
    >>> list(_sequences(mask))
    [(1, 3)]
    >>> mask = np.array([True, False, False, True])
    >>> list(_sequences(mask))
    [(0, 1), (3, 4)]
    >>> mask = np.ones((4,), dtype=bool)
    >>> list(_sequences(mask))
    [(0, 4)]
    >>> mask = np.zeros((4,), dtype=bool)
    >>> list(_sequences(mask))
    []
    """
    if not np.any(mask):
        # There are no sequences in this mask
        return izip([], [])
    if isinstance(mask, np.ma.MaskedArray):
        mask = mask.filled(False)

    start_indices = np.flatnonzero(
        np.ediff1d(mask.astype(int), to_begin=0) == 1)
    end_indices = np.flatnonzero(
        np.ediff1d(mask.astype(int), to_begin=0) == -1)

    # If the mask starts or ends with a True value this needs to be handled
    # separately:
    if (start_indices.size == 0 or
            (end_indices.size != 0 and end_indices[0] < start_indices[0])):
        start_indices = np.insert(start_indices, 0, 0)
    if (end_indices.size == 0 or
            (start_indices.size != 0 and start_indices[-1] > end_indices[-1])):
        end_indices = np.append(end_indices, len(mask))
    return ((int(s), int(e)) for s, e in izip(start_indices, end_indices))


class Logics(object):
    @staticmethod
    def first(mask):
        """
        Return a new array which is True only at the very first position
        where mask was True.

        Parameters
        ----------
        mask : array_like
            The array the function should be performed on.

        Returns
        -------
        np.array
            An array with the same length and dtype as mask.
        """
        newmask = np.zeros_like(mask)
        indices = np.flatnonzero(mask)
        if len(indices):
            newmask[indices[0]] = True
        if isinstance(newmask, np.ma.MaskedArray):
            newmask = newmask.filled(False)
        return newmask

    @staticmethod
    def last(mask):
        """
        Return a new array which is True only at the very last position
        where mask was True.

        Parameters
        ----------
        mask: array_like
            The array the function should be performed on.

        Returns
        -------
        np.array
            An array with the same length and dtype as mask.
        """
        newmask = np.zeros_like(mask)
        indices = np.flatnonzero(mask)
        if len(indices):
            newmask[indices[-1]] = True
        if isinstance(newmask, np.ma.MaskedArray):
            newmask = newmask.filled(False)
        return newmask

    @staticmethod
    def shift_array(mask, shift_value):
        """
        Return a new mask with values shifted by shift_value
        compared to mask. shift_value can be any integer.

        mask : array_like
            A numpy array with booleans.
        shift_value : int
            The number of positions that mask should be shifted by.

        Returns
        -------
        np.array
            An array of booleans with the same length as mask.
        """
        if shift_value == 0:
            return mask
        if abs(shift_value) >= len(mask):
            return np.ma.masked_all_like(mask)
        if not isinstance(mask, np.ndarray):
            np.array(mask)

        new_values = np.ma.masked_all((abs(shift_value),), dtype=bool)
        if shift_value > 0:
            return np.ma.concatenate((new_values, mask[:-shift_value]))
        else:
            return np.ma.concatenate((mask[abs(shift_value):], new_values))

    @staticmethod
    def shift_seq_start(mask, shift_value):
        """
        Return a mask whose sequences of True values start shift_value
        values later than the sequences in mask, but end on the same value as
        the original sequence in mask. As a consequence, if shift_value is
        positive, sequences shorter than or equal to shift_value will
        disappear.

        mask : array_like
            A numpy array with booleans.
        shift_value : int
            The number of positions that mask should be shifted by.

        Returns
        -------
        np.array
            An array with the same length and dtype as mask.

        Examples
        --------
        >>> mask = np.array(
            [True, True, False, False, True, True, True, False])
        >>> shift_seq_start(mask, 2)
        array([
            False, False, False, False, False, False,  True, False],
            dtype=bool)
        >>> shift_seq_start(mask, -1)
        array([True, True, False, True, True, True, True, False], dtype=bool)
        """
        if isinstance(mask, np.ma.MaskedArray):
            newmask = np.ma.zeros(mask.shape, dtype=bool)
            newmask.mask = mask.mask
        else:
            newmask = np.zeros_like(mask)
        for start_index, end_index in find_sequences_indices(mask):
            # Protection needed when shift_value is a big enough negative value
            new_start_index = max(start_index + shift_value, 0)
            # This doesn't do anything if new_start_index > end_index
            newmask[new_start_index:end_index] = True
        return newmask

    @staticmethod
    def shift_seq_end(mask, shift_value):
        """
        Return a mask whose sequences of True values start on the same value
        as the original sequence in mask, but end shift_value values later than
        the sequences in mask. As a consequence, if shift_value is negative,
        sequences shorter than or equal to shift_value will disappear.

        Parameters
        ----------
        mask : array_like
            A numpy array with booleans.
        shift_value : int
            The number of positions that mask should be shifted by.

        Returns
        -------
        np.array
            An array with the same length and dtype as mask.

        Examples
        --------
        >>> mask = np.array([True, False, False, False, True, True, False])
        >>> shift_seq_end(mask, 2)
        array([True, True, True, False, True, True, True], dtype=bool)
        >>> shift_seq_end(mask, -1)
        array([False, False, False, False, True, False, False], dtype=bool)
        """
        if isinstance(mask, np.ma.MaskedArray):
            newmask = np.ma.zeros(mask.shape, dtype=bool)
            newmask.mask = mask.mask
        else:
            newmask = np.zeros_like(mask)
        for start_index, end_index in find_sequences_indices(mask):
            # Protection needed when shift_value is a big enough negative value
            if end_index + shift_value >= 0:
                # This doesn't do anything if
                # start_index > end_index + shift_value
                newmask[start_index:end_index + shift_value] = True
        return newmask


    @staticmethod
    def shift_seq_start_end(mask, start_shift, end_shift):
        """
        Return a mask whose sequences of True values start start_shift
        values later than the sequences in mask, and end end_shift
        values later than the mask. As a consequence: if both shift
        values are equal and positive then the mask is shiften to the
        right; if equal and negative then the mask shifts to the left;
        if the start shift is bigger than the end shift then any true sequences
        becomes smaller; and if the start shift is smaller than the
        end shift then any such sequences becomes bigger.

        This function differs from performing shift_seq_start followed
        by shift_seq_end (or the opposite order) since it handles both
        endpoints simultaneously.

        mask : array_like
            A numpy array with booleans.
        start_shift : int
            The number of positions that the start of sequences should be shifted by.
        end_shift : int
            The number of positions that the end of sequences should be shifted by.

        Returns
        -------
        np.array
            An array with the same length and dtype as mask.

        Examples
        --------
        >>> mask = np.array(
            [True, True, False, False, True, True, True, False])
        >>> shift_seq_start_end(mask, 2, 1)
        array([
            False, False, True, False, False, False,  True, True],
            dtype=bool)
        >>> shift_seq_start_end(mask, 0, -1)
        array([True, False, False, False, True, True, False, False], dtype=bool)

        """
        if isinstance(mask, np.ma.MaskedArray):
            newmask = np.ma.zeros(mask.shape, dtype=bool)
            newmask.mask = mask.mask
        else:
            newmask = np.zeros_like(mask)
        for start_index, end_index in find_sequences_indices(mask):
            # Protection needed when shift_value is a big enough negative value
            new_start_index = max(start_index + start_shift, 0)
            new_end_index = max(end_index + end_shift, 0)
            # This doesn't do anything if new_start_index > end_index
            newmask[new_start_index:new_end_index] = True
        return newmask

    @staticmethod
    def find_seq(mask):
        """
        Returns a 2D-array with start and ending points for all sequences of
        true values in the input mask. This array cannot be the output directly
        for a column, but can be passed to gen_seq or be indexed to pick out
        the start or ending points.

        Examples
        --------
        >>> mask = np.array(
            [True, True, False, False, True, True, True, False])
        >>> find_seq(mask)
        array([[0,2],
               [4,6]], dtype=int)
        >>> find_seq(mask)[:,0]
        array([0, 4], dtype=int)
        >>> gen_seq(find_seq(mask)[[-1]], len(mask))  # Keep only last sequence
        >>> mask = np.array(
            [False, False, False, False, True, True, True, False])
        """
        return np.array(list(find_sequences_indices(mask)))

    @staticmethod
    def gen_seq(indices, length):
        """
        Generates a mask from a 2D array containing start and stop indices of
        the positions where the array should be true.

        Examples:
        ---------
        >>> gen_seq(np.array([[0,2],[3,4]]), 4)
        array([True, True, False, True])

        # This skips the first sequence but keeps the rest
        >>> gen_seq(find_seq([True, False, True, True, False, False])[1:], 6)
        array([False, False, True, True, False, False])
        """
        mask = np.zeros(length).astype(bool)
        for start_index, end_index in indices:
            mask[start_index:end_index] = True
        return mask


GUI_DICT = {
    "Logic functions": [
        ("Last", "ca.last(${signal0})", inspect.getdoc(Logics.last)),
        ("First", "ca.first(${signal0})", inspect.getdoc(Logics.first)),
        ("Shift array", "ca.shift_array(${signal0}, shift_value)",
         inspect.getdoc(Logics.shift_array)),
        ("Shift sequence start",
         "ca.shift_seq_start(${signal0}, shift_value)",
         inspect.getdoc(Logics.shift_seq_start)),
        ("Shift sequence end", "ca.shift_seq_end(${signal0}, shift_value)",
         inspect.getdoc(Logics.shift_seq_end)),
        ("Shift sequence start end",
         "ca.shift_seq_start_end(${signal0}, start_shift, end_shift)",
         inspect.getdoc(Logics.shift_seq_start_end)),
        ("Find indices for sequence", "ca.find_seq(${signal0})",
         inspect.getdoc(Logics.find_seq)),
        ("Generate mask from indices", "ca.gen_seq(signal_mask, length)",
         inspect.getdoc(Logics.gen_seq)),
    ]
}
