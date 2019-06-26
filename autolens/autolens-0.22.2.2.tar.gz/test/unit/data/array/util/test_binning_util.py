import os
import shutil
import numpy as np
import pytest

from autolens.data.array.util import binning_util


class TestBinnedPaddingArray:

    def test__bin_up_factor_is_1__array_2d_does_not_change_shape(self):

        array_2d = np.array([[1.0, 2.0, 3.0],
                             [4.0, 5.0, 6.0],
                             [7.0, 8.0, 9.0]])

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=1)

        assert (array_2d_padded == array_2d).all()

    def test__bin_up_factor_gives_no_remainder__array_2d_does_not_change_shape(self):

        array_2d = np.ones(shape=(6, 6))

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)
        assert array_2d_padded.shape == (6, 6)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert array_2d_padded.shape == (6, 6)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=6)
        assert array_2d_padded.shape == (6, 6)

        array_2d = np.ones(shape=(8, 8))

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)
        assert array_2d_padded.shape == (8, 8)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=4)
        assert array_2d_padded.shape == (8, 8)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=8)
        assert array_2d_padded.shape == (8, 8)

        array_2d = np.ones(shape=(9, 9))

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert array_2d_padded.shape == (9, 9)

        array_2d = np.ones(shape=(16, 16))

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)
        assert array_2d_padded.shape == (16, 16)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=4)
        assert array_2d_padded.shape == (16, 16)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=8)
        assert array_2d_padded.shape == (16, 16)

        array_2d = np.ones(shape=(12, 16))

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)
        assert array_2d_padded.shape == (12, 16)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=4)
        assert array_2d_padded.shape == (12, 16)

        array_2d = np.ones(shape=(16, 12))

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)
        assert array_2d_padded.shape == (16, 12)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=4)
        assert array_2d_padded.shape == (16, 12)

    def test__bin_up_factor_gives_remainder__array_2d_padded_to_give_no_remainder(self):

        array_2d = np.ones(shape=(6, 6))

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=4)
        assert array_2d_padded.shape == (8, 8)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=5)
        assert array_2d_padded.shape == (10, 10)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=7)
        assert array_2d_padded.shape == (7, 7)

        array_2d = np.ones(shape=(10, 10))

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert array_2d_padded.shape == (12, 12)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=4)
        assert array_2d_padded.shape == (12, 12)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=6)
        assert array_2d_padded.shape == (12, 12)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=7)
        assert array_2d_padded.shape == (14, 14)

        array_2d = np.ones(shape=(7, 10))

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert array_2d_padded.shape == (9, 12)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=5)
        assert array_2d_padded.shape == (10, 10)

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=7)
        assert array_2d_padded.shape == (7, 14)

    def test__padding_using_arrays_and_not_shapes(self):

        array_2d = np.ones(shape=(4, 4))
        array_2d[1 ,1] = 2.0

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert array_2d_padded.shape == (6, 6)
        assert (array_2d_padded == np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                                             [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
                                             [0.0, 1.0, 2.0, 1.0, 1.0, 0.0],
                                             [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
                                             [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
                                             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])).all()

        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=5)
        assert array_2d_padded.shape == (5, 5)
        assert (array_2d_padded == np.array([[1.0, 1.0, 1.0, 1.0, 0.0],
                                             [1.0, 2.0, 1.0, 1.0, 0.0],
                                             [1.0, 1.0, 1.0, 1.0, 0.0],
                                             [1.0, 1.0, 1.0, 1.0, 0.0],
                                             [0.0, 0.0, 0.0, 0.0, 0.0]])).all()

        array_2d = np.ones(shape=(2, 3))
        array_2d[1 ,1] = 2.0
        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)
        assert array_2d_padded.shape == (2, 4)
        assert (array_2d_padded == np.array([[0.0, 1.0, 1.0, 1.0],
                                             [0.0, 1.0, 2.0, 1.0]])).all()

        array_2d = np.ones(shape=(3, 2))
        array_2d[1 ,1] = 2.0
        array_2d_padded = binning_util.padded_binning_array_2d_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)
        assert array_2d_padded.shape == (4, 2)
        assert (array_2d_padded == np.array([[0.0, 0.0],
                                             [1.0, 1.0],
                                             [1.0, 2.0],
                                             [1.0, 1.0]])).all()


class TestBinnedArrays2d:

    def test__bin_using_mean__array_4x4_to_2x2__uses_mean_correctly(self):

        array_2d = np.array([[1.0, 1.0, 2.0, 2.0],
                             [1.0, 1.0, 2.0, 2.0],
                             [3.0, 3.0, 4.0, 4.0],
                             [3.0, 3.0, 4.0, 4.0]])

        binned_array_2d = binning_util.binned_up_array_2d_using_mean_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)

        assert (binned_array_2d == np.array([[1.0, 2.0],
                                             [3.0, 4.0]])).all()

        array_2d = np.array([[1.0, 2.0, 2.0, 2.0],
                             [1.0, 6.0, 2.0, 10.0],
                             [9.0, 3.0, 4.0, 0.0],
                             [3.0, 3.0, 4.0, 4.0]])

        binned_array_2d = binning_util.binned_up_array_2d_using_mean_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)

        assert (binned_array_2d == np.array([[2.5, 4.0],
                                             [4.5, 3.0]])).all()

    def test__bin_using_mean__array_6x3_to_2x1_and_3x6_to_1x2__uses_mean_correctly(self):

        array_2d = np.array([[1.0, 1.0, 1.0],
                             [1.0, 1.0, 1.0],
                             [1.0, 1.0, 1.0],
                             [2.0, 2.0, 2.0],
                             [2.0, 2.0, 2.0],
                             [2.0, 2.0, 2.0]])

        binned_array_2d = binning_util.binned_up_array_2d_using_mean_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)

        assert (binned_array_2d == np.array([[1.0],
                                             [2.0]])).all()

        array_2d = np.array([[1.0, 1.0, 1.0],
                             [1.0, 10.0, 1.0],
                             [1.0, 1.0, 1.0],
                             [2.0, 11.0, 2.0],
                             [2.0, 2.0, 2.0],
                             [2.0, 2.0, 2.0]])

        binned_array_2d = binning_util.binned_up_array_2d_using_mean_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert (binned_array_2d == np.array([[2.0],
                                             [3.0]])).all()

        array_2d = np.array([[1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
                             [1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
                             [1.0, 1.0, 1.0, 2.0, 2.0, 2.0]])

        binned_array_2d = binning_util.binned_up_array_2d_using_mean_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert (binned_array_2d == np.array([[1.0, 2.0]])).all()

        array_2d = np.array([[1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
                             [1.0, 10.0, 1.0, 11.0, 2.0, 2.0],
                             [1.0, 1.0, 1.0, 2.0, 2.0, 2.0]])

        binned_array_2d = binning_util.binned_up_array_2d_using_mean_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert (binned_array_2d == np.array([[2.0, 3.0]])).all()

    def test__bin_using_mean__bin_includes_padding_image_with_zeros(self):

        # Padded array:

        # [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        #  [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        #  [0.0, 1.0, 2.0, 1.0, 1.0, 0.0],
        #  [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        #  [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        #  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

        array_2d = np.ones(shape=(4, 4))
        array_2d[1 ,1] = 2.0
        binned_array_2d = binning_util.binned_up_array_2d_using_mean_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert (binned_array_2d == np.array([[(5.0 / 9.0), (4.0 / 9.0)],
                                             [(4.0 / 9.0), (4.0 / 9.0)]])).all()

        # Padded Array:

        # np.array([[0.0, 1.0, 1.0, 1.0],
        #           [0.0, 1.0, 2.0, 1.0]]

        array_2d = np.ones(shape=(2, 3))
        array_2d[1 ,1] = 2.0
        binned_2d_array = binning_util.binned_up_array_2d_using_mean_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)
        assert (binned_2d_array == np.array([[0.5, 1.25]])).all()

    def test__bin_using_quadrature__array_4x4_to_2x2__uses_quadrature_correctly(self):

        array_2d = np.array([[1.0, 1.0, 2.0, 2.0],
                             [1.0, 1.0, 2.0, 2.0],
                             [3.0, 3.0, 4.0, 4.0],
                             [3.0, 3.0, 4.0, 4.0]])

        binned_array_2d = binning_util.binned_array_2d_using_quadrature_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)

        assert (binned_array_2d == np.array([[np.sqrt(4.0) / 4.0, np.sqrt(16.0) / 4.0],
                                             [np.sqrt(36.0) / 4.0, np.sqrt(64.0) / 4.0]])).all()

        array_2d = np.array([[1.0, 2.0, 2.0, 2.0],
                             [1.0, 6.0, 2.0, 10.0],
                             [9.0, 3.0, 4.0, 0.0],
                             [3.0, 3.0, 4.0, 4.0]])

        binned_array_2d = binning_util.binned_array_2d_using_quadrature_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)

        assert (binned_array_2d == np.array([[np.sqrt(42.0) / 4.0, np.sqrt(112.0) / 4.0],
                                             [np.sqrt(108.0) / 4.0, np.sqrt(48.0) / 4.0]])).all()

    def test__bin_using_quadrature__array_6x3_to_2x1_and_3x6_to_1x2__uses_quadrature_correctly(self):

        array_2d = np.array([[1.0, 1.0, 1.0],
                             [1.0, 1.0, 1.0],
                             [1.0, 1.0, 1.0],
                             [2.0, 2.0, 2.0],
                             [2.0, 2.0, 2.0],
                             [2.0, 2.0, 2.0]])

        binned_array_2d = binning_util.binned_array_2d_using_quadrature_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)

        assert (binned_array_2d == np.array([[np.sqrt(9.0) / 9.0],
                                             [np.sqrt(36.0) / 9.0]])).all()

        array_2d = np.array([[1.0, 1.0, 1.0],
                             [1.0, 10.0, 1.0],
                             [1.0, 1.0, 1.0],
                             [2.0, 4.0, 2.0],
                             [2.0, 2.0, 2.0],
                             [2.0, 2.0, 2.0]])

        binned_array_2d = binning_util.binned_array_2d_using_quadrature_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert (binned_array_2d == np.array([[np.sqrt(108.0) / 9.0],
                                             [np.sqrt(48.0) / 9.0]])).all()

        array_2d = np.array([[1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
                             [1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
                             [1.0, 1.0, 1.0, 2.0, 2.0, 2.0]])

        binned_array_2d = binning_util.binned_array_2d_using_quadrature_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert (binned_array_2d == np.array([[np.sqrt(9.0) / 9.0, np.sqrt(36.0) / 9.0]])).all()

        array_2d = np.array([[1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
                             [1.0, 10.0, 1.0, 4.0, 2.0, 2.0],
                             [1.0, 1.0, 1.0, 2.0, 2.0, 2.0]])

        binned_array_2d = binning_util.binned_array_2d_using_quadrature_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert (binned_array_2d == np.array([[np.sqrt(108.0) / 9.0, np.sqrt(48.0) / 9.0]])).all()

    def test__bin_using_quadrature__bin_includes_padding_image_with_zeros(self):

        # Padded array:

        # [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        #  [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        #  [0.0, 1.0, 2.0, 1.0, 1.0, 0.0],
        #  [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        #  [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        #  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

        array_2d = np.ones(shape=(4, 4))
        array_2d[1 ,1] = 2.0
        binned_array_2d = binning_util.binned_array_2d_using_quadrature_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert (binned_array_2d == np.array([[np.sqrt(7.0) / 9.0, np.sqrt(4.0) / 9.0],
                                             [np.sqrt(4.0) / 9.0, np.sqrt(4.0) / 9.0]])).all()

        # Padded Array:

        # np.array([[0.0, 1.0, 1.0, 1.0],
        #           [0.0, 1.0, 2.0, 1.0]]

        array_2d = np.ones(shape=(2, 3))
        array_2d[1 ,1] = 2.0
        binned_2d_array = binning_util.binned_array_2d_using_quadrature_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)
        assert (binned_2d_array == np.array([[np.sqrt(2.0) / 4.0, np.sqrt(7.0) / 4.0]])).all()

    def test__bin_using_sum__array_4x4_to_2x2__uses_sum_correctly(self):

        array_2d = np.array([[1.0, 1.0, 2.0, 2.0],
                             [1.0, 1.0, 2.0, 2.0],
                             [3.0, 3.0, 4.0, 4.0],
                             [3.0, 3.0, 4.0, 4.0]])

        binned_array_2d = binning_util.binned_array_2d_using_sum_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)

        assert (binned_array_2d == np.array([[4.0, 8.0],
                                             [12.0, 16.0]])).all()

        array_2d = np.array([[1.0, 2.0, 2.0, 2.0],
                             [1.0, 6.0, 2.0, 10.0],
                             [9.0, 3.0, 4.0, 0.0],
                             [3.0, 3.0, 4.0, 4.0]])

        binned_array_2d = binning_util.binned_array_2d_using_sum_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)

        assert (binned_array_2d == np.array([[10.0, 16.0],
                                             [18.0, 12.0]])).all()

    def test__bin_using_sum__array_6x3_to_2x1_and_3x6_to_1x2__uses_sum_correctly(self):

        array_2d = np.array([[1.0, 1.0, 1.0],
                             [1.0, 1.0, 1.0],
                             [1.0, 1.0, 1.0],
                             [2.0, 2.0, 2.0],
                             [2.0, 2.0, 2.0],
                             [2.0, 2.0, 2.0]])

        binned_array_2d = binning_util.binned_array_2d_using_sum_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)

        assert (binned_array_2d == np.array([[9.0],
                                             [18.0]])).all()

        array_2d = np.array([[1.0, 1.0, 1.0],
                             [1.0, 10.0, 1.0],
                             [1.0, 1.0, 1.0],
                             [2.0, 11.0, 2.0],
                             [2.0, 2.0, 2.0],
                             [2.0, 2.0, 2.0]])

        binned_array_2d = binning_util.binned_array_2d_using_sum_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert (binned_array_2d == np.array([[18.0],
                                             [27.0]])).all()

        array_2d = np.array([[1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
                             [1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
                             [1.0, 1.0, 1.0, 2.0, 2.0, 2.0]])

        binned_array_2d = binning_util.binned_array_2d_using_sum_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert (binned_array_2d == np.array([[9.0, 18.0]])).all()

        array_2d = np.array([[1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
                             [1.0, 10.0, 1.0, 11.0, 2.0, 2.0],
                             [1.0, 1.0, 1.0, 2.0, 2.0, 2.0]])

        binned_array_2d = binning_util.binned_array_2d_using_sum_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert (binned_array_2d == np.array([[18.0, 27.0]])).all()

    def test__bin_using_sum__bin_includes_padding_image_with_zeros(self):

        # Padded array:

        # [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        #  [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        #  [0.0, 1.0, 2.0, 1.0, 1.0, 0.0],
        #  [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        #  [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        #  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

        array_2d = np.ones(shape=(4, 4))
        array_2d[1 ,1] = 2.0
        binned_array_2d = binning_util.binned_array_2d_using_sum_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=3)
        assert (binned_array_2d == np.array([[5.0, 4.0],
                                             [4.0, 4.0]])).all()

        # Padded Array:

        # np.array([[0.0, 1.0, 1.0, 1.0],
        #           [0.0, 1.0, 2.0, 1.0]]

        array_2d = np.ones(shape=(2, 3))
        array_2d[1 ,1] = 2.0
        binned_2d_array = binning_util.binned_array_2d_using_sum_from_array_2d_and_bin_up_factor(
            array_2d=array_2d, bin_up_factor=2)
        assert (binned_2d_array == np.array([[2.0, 5.0]])).all()
        
        
class TestBinUpMask2d:

    def test__mask_4x4_to_2x2__creates_correct_binned_up_mask(self):

        mask_2d = np.array([[True, False, True, True],
                            [True, True, True, True],
                            [True, True, False, False],
                            [False, True, True, True]])

        binned_mask_2d = binning_util.binned_up_mask_2d_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=2)

        assert (binned_mask_2d == np.array([[False, True],
                                            [False, False]])).all()

        mask_2d = np.array([[True, True, True, True],
                            [True, True, True, True],
                            [True, True, False, False],
                            [True, True, True, True]])

        binned_mask_2d = binning_util.binned_up_mask_2d_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=2)

        assert (binned_mask_2d == np.array([[True, True],
                                            [True, False]])).all()

    def test__mask_6x3_to_2x1_and_3x6_to_1x2__sets_up_correct_mask(self):

        mask_2d = np.array([[True, True, True],
                            [True, True, True],
                            [True, True, True],
                            [True, True, True],
                            [True, True, True],
                            [True, True, True]])

        binned_mask_2d = binning_util.binned_up_mask_2d_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=3)

        assert (binned_mask_2d == np.array([[True],
                                            [True]])).all()

        mask_2d = np.array([[True, True, True],
                            [True, True, False],
                            [True, True, True],
                            [True, True, True],
                            [True, True, True],
                            [True, True, True]])

        binned_mask_2d = binning_util.binned_up_mask_2d_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=3)
        assert (binned_mask_2d == np.array([[False],
                                            [True]])).all()

        mask_2d = np.array([[True, True, True, True, True, True],
                            [True, True, True, True, True, True],
                            [True, True, True, True, True, True]])

        binned_mask_2d = binning_util.binned_up_mask_2d_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=3)
        assert (binned_mask_2d == np.array([[True, True]])).all()

        mask_2d = np.array([[True, True, True, True, True, True],
                            [True, True, True, True, True, True],
                            [True, True, True, True, True, False]])

        binned_mask_2d = binning_util.binned_up_mask_2d_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=3)
        assert (binned_mask_2d == np.array([[True, False]])).all()

    def test__bin_includes_padding_image_with_zeros(self):
        # Padded mask:

        # [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        #  [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        #  [0.0, 1.0, 2.0, 1.0, 1.0, 0.0],
        #  [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        #  [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        #  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

        mask_2d = np.full(shape=(4, 4), fill_value=True)
        mask_2d[1, 1] = False
        mask_2d[3, 3] = False
        binned_mask_2d = binning_util.binned_up_mask_2d_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=3)
        assert (binned_mask_2d == np.array([[False, True],
                                            [True, False]])).all()

        # Padded Array:

        # np.array([[0.0, 1.0, 1.0, 1.0],
        #           [0.0, 1.0, 2.0, 1.0]]

        mask_2d = np.full(shape=(2, 3), fill_value=True)
        mask_2d[1, 2] = False
        binned_2d_mask = binning_util.binned_up_mask_2d_from_mask_2d_and_bin_up_factor(mask_2d=mask_2d, bin_up_factor=2)
        assert (binned_2d_mask == np.array([[True, False]])).all()


class TestBinnedMask2dMapperAndBinnedMaskedArrayToMaskedArray:

    def test__masks_are_full_arrays_and_bin_up_factor_2__mapping_is_correct(self):

        mask_2d = np.full(fill_value=False, shape=(4,4))

        binned_mask_2d_mapper = \
            binning_util.binned_mask_2d_mapper_from_mask_2d_and_bin_up_factor(
            mask_2d=mask_2d, bin_up_factor=2)

        assert (binned_mask_2d_mapper == np.array([[False, True, False, True],
                                                   [True, True, True, True],
                                                   [False, True, False, True],
                                                   [True, True, True, True]])).all()

        binned_masked_array_1d_to_masked_array_1d = \
            binning_util.binned_masked_array_1d_to_masked_array_1d_from_mask_2d_and_bin_up_factor(
            mask_2d=mask_2d, bin_up_factor=2)

        assert (binned_masked_array_1d_to_masked_array_1d == np.array([0, 2, 8, 10])).all()

        mask_2d = np.full(fill_value=False, shape=(9,9))

        binned_mask_2d_mapper = \
            binning_util.binned_mask_2d_mapper_from_mask_2d_and_bin_up_factor(
                mask_2d=mask_2d, bin_up_factor=3)

        assert (binned_mask_2d_mapper == np.array([[False, True, True, False, True, True, False, True, True],
                                                   [True, True, True, True, True, True, True, True, True],
                                                   [True, True, True, True, True, True, True, True, True],
                                                   [False, True, True, False, True, True, False, True, True],
                                                   [True, True, True, True, True, True, True, True, True],
                                                   [True, True, True, True, True, True, True, True, True],
                                                   [False, True, True, False, True, True, False, True, True],
                                                   [True, True, True, True, True, True, True, True, True],
                                                   [True, True, True, True, True, True, True, True, True],])).all()

        binned_masked_array_1d_to_masked_array_1d = \
            binning_util.binned_masked_array_1d_to_masked_array_1d_from_mask_2d_and_bin_up_factor(
            mask_2d=mask_2d, bin_up_factor=3)

        assert (binned_masked_array_1d_to_masked_array_1d == np.array([0, 3, 6, 27, 30, 33, 54, 57, 60])).all()

    def test__masks_are_rectangular_arrays__include_areas_which_bin_up_is_all_true(self):

        mask_2d = np.array([[True, False, True, True, True, True],
                            [False, False, False, True, True, True]])

        binned_mask_2d_mapper = \
            binning_util.binned_mask_2d_mapper_from_mask_2d_and_bin_up_factor(
            mask_2d=mask_2d, bin_up_factor=2)


        assert (binned_mask_2d_mapper == np.array([[True, False, True, True, True, True],
                                                   [True, True, False, True, True, True]])).all()

        binned_masked_array_1d_to_masked_array_1d = \
            binning_util.binned_masked_array_1d_to_masked_array_1d_from_mask_2d_and_bin_up_factor(
            mask_2d=mask_2d, bin_up_factor=2)

        assert (binned_masked_array_1d_to_masked_array_1d == np.array([0, 3])).all()

        mask_2d = np.array([[True, False],
                            [False, False],
                            [False, True],
                            [True, True],
                            [True, True],
                            [True, True]])

        binned_mask_2d_mapper = \
            binning_util.binned_mask_2d_mapper_from_mask_2d_and_bin_up_factor(
            mask_2d=mask_2d, bin_up_factor=2)

        assert (binned_mask_2d_mapper == np.array([[True, False],
                                                    [True, True],
                                                    [False, True],
                                                    [True, True],
                                                    [True, True],
                                                    [True, True]])).all()

        binned_masked_array_1d_to_masked_array_1d = \
            binning_util.binned_masked_array_1d_to_masked_array_1d_from_mask_2d_and_bin_up_factor(
            mask_2d=mask_2d, bin_up_factor=2)

        assert (binned_masked_array_1d_to_masked_array_1d == np.array([0, 3])).all()

    def test__mask_includes_padding__mapper_mask_accounts_for_padding(self):

        mask_2d = np.full(fill_value=False, shape=(5,5))

        binned_mask_2d_mapper = \
            binning_util.binned_mask_2d_mapper_from_mask_2d_and_bin_up_factor(
            mask_2d=mask_2d, bin_up_factor=2)

        assert (binned_mask_2d_mapper == np.array([[True, True, True, True, True, True],
                                                   [True, False, False, True, False, True],
                                                   [True, False, False, True, False, True],
                                                   [True, True, True, True, True, True],
                                                   [True, False, False, True, False, True],
                                                   [True, True, True, True, True, True]])).all()

        binned_masked_array_1d_to_masked_array_1d = \
            binning_util.binned_masked_array_1d_to_masked_array_1d_from_mask_2d_and_bin_up_factor(
            mask_2d=mask_2d, bin_up_factor=2)

        assert (binned_masked_array_1d_to_masked_array_1d == np.array([0, 1, 3, 5, 6, 8, 15, 16, 18])).all()
