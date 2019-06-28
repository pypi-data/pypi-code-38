# -*- coding: utf-8 -*-
#  This file is part of QAMpy.
#
#  QAMpy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Foobar is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with QAMpy.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 Jochen Schröder, Mikael Mazur

# These two functions from QamPy library


import warnings
from numba.types import float64
import numpy as np
import numba

N = np

""" a number of convenience functions"""


def normal_sample(samples):
    '''

    :param samples: 1d array or 2d array
    :return: normalized samples
    '''
    assert isinstance(samples,np.ndarray)
    ndim = samples.ndim
    samples = np.atleast_2d(samples)
    samples_new = np.zeros_like(samples,dtype=samples.dtype)
    cnt = 0
    for row in samples:
        row = row / np.sqrt(np.mean(row.real ** 2 + row.imag ** 2))
        samples_new[cnt,:] = row
        cnt = cnt+1
    if ndim ==1:
        samples_new = samples_new[0,:]
    return samples_new


@numba.jit(cache=True)
def segment_axis(a, length, overlap, mode='cut', append_to_end=0):
    """
        Generate a new array that chops the given array along the given axis into
        overlapping frames.

        example:
        >>> segment_axis(arange(10), 4, 2)
        array([[0, 1, 2, 3],
               [2, 3, 4, 5],
               [4, 5, 6, 7],
               [6, 7, 8, 9]])

        arguments:
        a       The array to segment must be 1d-array
        length  The length of each frame
        overlap The number of array elements by which the frames should overlap

        end     What to do with the last frame, if the array is not evenly
                divisible into pieces. Options are:

                'cut'   Simply discard the extra values
                'pad'   Pad with a constant value

        append_to_end:    The value to use for end='pad'

        a new array will be returned.

    """

    if a.ndim !=1:
        raise Exception("Error, input array must be 1d")
    if overlap > length:
        raise Exception("overlap cannot exceed the whole length")

    stride = length - overlap
    row = 1
    total_number = length
    while True:
        total_number = total_number + stride
        if total_number > len(a):
            break
        else:
            row = row + 1

    # 一共要分成row行
    if total_number > len(a):
        if mode == 'cut':
            b = np.zeros((row, length), dtype=np.complex128)
            is_append_to_end = False
        else:
            b = np.zeros((row + 1, length), dtype=np.complex128)
            is_append_to_end = True
    else:
        b = np.zeros((row, length), dtype=np.complex128)
        is_append_to_end = False

    index = 0
    for i in range(row):
        b[i, :] = a[index:index + length]
        index = index + stride

    if is_append_to_end:
        last = a[index:]

        b[row, 0:len(last)] = last
        b[row, len(last):] = append_to_end

    return b


def bin2gray(value):
    """
    Convert a binary value to an gray coded value see _[1]. This also works for arrays.
    ..[1] https://en.wikipedia.org/wiki/Gray_code#Constructing_an_n-bit_Gray_code
    """
    return value ^ (value >> 1)



@numba.guvectorize([(numba.types.complex128[:],numba.types.complex128[:],numba.types.complex128[:])], '(n),(m)->(n)',nopython=True)
def exp_decision(symbol,const,res):
    for index,sym in enumerate(symbol):
        # distance = sym-const
        distance = np.abs(sym-const)
        res[index] = const[np.argmin(distance)]




@numba.jit(cache=True)
def decision(symbol, constl):
    '''
        constl must be 2d
    '''
    if constl.ndim !=2:
        raise Exception("constl input to decision must be 2d")
    distance = np.abs(constl[0] - symbol)
    decision = constl[0, np.argmin(distance)]

    return decision


def cal_symbols_qam(M):
    """
    Generate the symbols on the constellation diagram for M-QAM
    """
    if np.log2(M) % 2 > 0.5:
        return cal_symbols_cross_qam(M)
    else:
        return cal_symbols_square_qam(M)


def cal_symbols_cross_qam(M):
    """
    Generate the symbols on the constellation diagram for non-square (cross) M-QAM
    """
    N = (np.log2(M) - 1) / 2
    s = 2 ** (N - 1)
    rect = np.mgrid[-(2 ** (N + 1) - 1):2 ** (N + 1) - 1:1.j * 2 ** (N + 1), -(
            2 ** N - 1):2 ** N - 1:1.j * 2 ** N]
    qam = rect[0] + 1.j * rect[1]
    idx1 = np.where((abs(qam.real) > 3 * s) & (abs(qam.imag) > s))
    idx2 = np.where((abs(qam.real) > 3 * s) & (abs(qam.imag) <= s))
    qam[idx1] = np.sign(qam[idx1].real) * (
            abs(qam[idx1].real) - 2 * s) + 1.j * (np.sign(qam[idx1].imag) *
                                                  (4 * s - abs(qam[idx1].imag)))
    qam[idx2] = np.sign(qam[idx2].real) * (
            4 * s - abs(qam[idx2].real)) + 1.j * (np.sign(qam[idx2].imag) *
                                                  (abs(qam[idx2].imag) + 2 * s))
    return qam.flatten()


def cal_symbols_square_qam(M):
    """
    Generate the symbols on the constellation diagram for square M-QAM
    """
    qam = np.mgrid[-(2 * np.sqrt(M) / 2 - 1):2 * np.sqrt(
        M) / 2 - 1:1.j * np.sqrt(M), -(2 * np.sqrt(M) / 2 - 1):2 * np.sqrt(M) /
                                                               2 - 1:1.j * np.sqrt(M)]
    return (qam[0] + 1.j * qam[1]).flatten()


def cal_scaling_factor_qam(M):
    """
    Calculate the scaling factor for normalising MQAM symbols to 1 average Power
    """
    bits = np.log2(M)
    if not bits % 2:
        scale = 2 / 3 * (M - 1)
    else:
        symbols = cal_symbols_qam(M)
        scale = (abs(symbols) ** 2).mean()
    return scale


def get_power(x):
    return np.mean(x.real ** 2 + x.imag ** 2)
