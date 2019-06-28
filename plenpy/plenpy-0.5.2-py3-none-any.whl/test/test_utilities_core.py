# Copyright (C) 2018-2019  The Plenpy Authors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Tests for plenpy.utilities.core module.
"""

import imageio
import numpy as np
from pytest import raises

import plenpy.logg
from plenpy import testing

from plenpy.utilities.core import BandInfo, SpectralArray, DimensionError


# Logging settings
logger = plenpy.logg.get_logger()
plenpy.logg.set_level("warning")

# Test data
TEST_HSI_FILENAME = "images/balloons.npy"
TEST_RGB_FILENAME = "images/balloons_RGB.png"
TEST_GREY_FILENAME = "images/balloons_GREY.png"


def test_band_info_init():
    """Test init of BandInfo class"""

    num_ch = 3
    centers = [100, 200, 300]
    unit = "nm"
    bandwidths = [1, 2, 3]
    centers_std = [0.1, 0.1, 0.2]
    bandwidths_std = [0.2, 0.3, 0.4]
    type = "reflectance"

    tmp = BandInfo(num_channels=num_ch, centers=centers, unit=unit,
                   bandwidths=bandwidths, bandwidths_std=bandwidths_std,
                   centers_std=centers_std, type=type)

    assert tmp.num_channels == num_ch
    assert tmp.centers == centers
    assert tmp.unit == unit
    assert tmp.bandwidths == bandwidths
    assert tmp.centers_std == centers_std
    assert tmp.bandwidths_std == bandwidths_std
    assert tmp.type == type

    return


def test_band_info_init_error():
    """Test init error of BandInfo class"""

    num_ch = 3
    centers = [100, 200]
    centers_true = [100, 200, 300]
    unit = "nm"
    bandwidths = [1, 2, 3, 5]
    centers_std = [0.1, 0.1, 0.2, 0.6, 0.2]
    bandwidths_std = [0.2, 0.3, 0.4, 1]
    type = "reflectance"

    # Test error handling
    with raises(ValueError) as cm:
        tmp = BandInfo(num_channels=num_ch, centers=centers, unit='nm')
    assert "Length of list has to match number of channels" == str(cm.value)

    with raises(ValueError) as cm:
        tmp = BandInfo(num_channels=num_ch, centers=centers_true,
                          bandwidths=bandwidths, unit='nm')
    assert "Length of list has to match number of channels" == str(cm.value)

    with raises(ValueError) as cm:
        tmp = BandInfo(num_channels=num_ch, centers=centers_true,
                          bandwidths_std=bandwidths_std, unit='nm')
    assert "Length of list has to match number of channels" == str(cm.value)

    with raises(ValueError) as cm:
        tmp = BandInfo(num_channels=num_ch, centers=centers_true,
                          centers_std=centers_std, unit='nm')
    assert "Length of list has to match number of channels" == str(cm.value)

    return


def test_band_info_equidistant():
    """Test ``from_equidistant`` class method.
    """

    tmp = BandInfo.from_equidistant(num_channels=5,
                                       lambda_start=400,
                                       lambda_end=800,
                                       bandwidth=0.5,
                                       center_std=1,
                                       bandwidth_std=0.7)

    assert tmp.num_channels == 5
    assert np.array_equal(tmp.centers,
                          np.asarray([400, 500, 600, 700, 800]))

    assert np.array_equal(tmp.bandwidths,
                          np.asarray([0.5, 0.5, 0.5, 0.5, 0.5]))

    assert np.array_equal(tmp.centers_std,
                          np.asarray([1, 1, 1, 1, 1]))

    assert np.array_equal(tmp.bandwidths_std,
                          np.asarray([0.7, 0.7, 0.7, 0.7, 0.7]))

    return


def test_band_info_eq_op():
    """Test eq operator
    """
    options = dict(num_channels=5, lambda_start=400, lambda_end=800,
                   bandwidth=0.5, center_std=1, bandwidth_std=0.7)

    # Create two BandInfo objects with same options
    tmp1 = BandInfo.from_equidistant(**options)
    tmp2 = BandInfo.from_equidistant(**options)

    assert tmp1 == tmp2

    return


def test_band_info_copy():
    """Test copy() of BandInfo class"""

    num_ch = 3
    centers = [100, 200, 300]
    unit = "nm"
    bandwidths = [1, 2, 3]
    centers_std = [0.1, 0.1, 0.2]
    bandwidths_std = [0.2, 0.3, 0.4]
    type = "reflectance"

    tmp = BandInfo(num_channels=num_ch, centers=centers, unit=unit,
                   bandwidths=bandwidths, bandwidths_std=bandwidths_std,
                   centers_std=centers_std, type=type)

    tmp_cp = tmp.copy()

    assert tmp == tmp_cp

    return


def test_spectral_array_errors():

    # Test input array type
    with raises(ValueError) as cm:
        tmp_arr = SpectralArray([1, 2, 3], dtype=np.float32, copy=True,
                                meta=None, band_info=None)
    assert "SpectralArray expects a numpy array." == str(cm.value)

    # Test input metadata type
    with raises(ValueError) as cm:
        tmp_arr = SpectralArray(np.asarray([1, 2, 3], dtype=np.uint8),
                                dtype=np.float32, copy=True,
                                meta="Not Meta", band_info=None)
    assert "SpectralArray expects meta data to be a dict." == str(cm.value)

    # Test input BandInfo type
    with raises(ValueError) as cm:
        tmp_arr = SpectralArray(np.asarray([1, 2, 3], dtype=np.uint8),
                                dtype=np.float32, copy=True,
                                meta=None, band_info="Not Bandinfo")
    assert "SpectralArray expects BandInfo or None instance." == str(cm.value)

    # Test input array size
    with raises(ValueError) as cm:
        tmp_arr = SpectralArray(np.asarray([], dtype=np.uint8),
                                dtype=np.float32, copy=True,
                                meta=None, band_info=None)
    assert "Invalid array size. Must have at least one axis." == str(cm.value)

    # Test invalid conversion
    with raises(ValueError) as cm:
        tmp_arr = SpectralArray(np.asarray([-1.0, 0.5, 1.0], dtype=np.float32),
                                dtype=np.float32, copy=True,
                                meta=None, band_info=None)
    assert "Array data out of range (0, 1)." == str(cm.value)

    with raises(ValueError) as cm:
        tmp_arr = SpectralArray(np.asarray([-127, 0, 127], dtype=np.int8),
                                dtype=np.float32, copy=True,
                                meta=None, band_info=None)
    assert "Array data out of range (0, 1)." == str(cm.value)

    # Test dtype argument
    with raises(ValueError) as cm:
        tmp_arr = SpectralArray(np.asarray([0.0, 0.1, 0.2], dtype=np.float32),
                                dtype=np.uint8, copy=True,
                                meta=None, band_info=None)
    assert "The passed dtype '<class 'numpy.uint8'>' is invalid. " \
           "Only numpy float types are allowed." == str(cm.value)

    # Test BandInfo compability
    info = BandInfo.from_equidistant(num_channels=10,
                                     lambda_start=400, lambda_end=700)
    arr = np.random.rand(5, 5, 11).astype(np.float32)

    with raises(ValueError) as cm:
        tmp_arr = SpectralArray(arr,
                                dtype=np.float32, copy=True,
                                meta=None, band_info=info)
    assert f"The numbers of channels of the band info object and the numbers "\
        f"of channels of the given data does not match. Found " \
        f"10 and 11 respectively." == str(cm.value)

    return


def test_spectral_array_new():

    num_ch = 10
    arr = np.random.rand(3, 3, num_ch).astype(np.float32)
    info = BandInfo.from_equidistant(num_channels=num_ch,
                                     lambda_start=400, lambda_end=70)
    meta = dict(entry="Entry", setting="Setting")

    tmp_arr = SpectralArray(arr, dtype=np.float32, copy=True,
                            meta=meta, band_info=info)

    assert np.array_equal(arr, tmp_arr)
    assert tmp_arr.num_channels == num_ch
    assert meta == tmp_arr.meta
    assert info == tmp_arr.band_info

    # Test Data conversion
    for dtype in [np.float16, np.float32, np.float64]:
        tmp_arr = SpectralArray(arr, dtype=dtype, copy=True)
        assert np.allclose(arr.astype(dtype), tmp_arr)

    return


def test_spectral_array_dtype_default():

    dtype_def = np.float32

    for d in [np.float16, np.float64, np.uint8]:
        arr = np.random.rand(5, 4, 3, 2).astype(d)
        tmp = SpectralArray(arr, dtype=None)
        assert tmp.dtype == dtype_def


def test_spectral_array_copy():
    """Test copying of SpectralArray"""

    num_ch = 10
    arr = np.random.rand(3, 3, num_ch).astype(np.float32)
    info = BandInfo.from_equidistant(num_channels=num_ch,
                                     lambda_start=400, lambda_end=70)
    meta = dict(entry="Entry", setting="Setting")

    tmp_arr = SpectralArray(arr, dtype=np.float32, copy=True,
                            meta=meta, band_info=info)

    tmp_arr_copy = tmp_arr.copy()

    assert np.array_equal(tmp_arr, tmp_arr_copy)
    assert tmp_arr.num_channels == tmp_arr_copy.num_channels
    assert tmp_arr.meta == tmp_arr_copy.meta
    assert tmp_arr.band_info == tmp_arr_copy.band_info

    return


def test_spectral_array_operations():
    num_ch = 10
    arr = np.random.rand(3, 3, num_ch).astype(np.float32)
    info = BandInfo.from_equidistant(num_channels=num_ch,
                                     lambda_start=400, lambda_end=70)
    meta = dict(entry="Entry", setting="Setting")

    tmp_arr = SpectralArray(arr, dtype=np.float32, copy=True,
                            meta=meta, band_info=info)

    # Multiplication
    tmp = 0.5*tmp_arr
    assert np.array_equal(0.5*arr, tmp)
    assert num_ch == tmp.num_channels
    assert meta == tmp.meta
    assert info == tmp.band_info

    # Addition
    tmp = tmp_arr + arr
    assert np.array_equal(2*arr, tmp)
    assert num_ch == tmp.num_channels
    assert meta == tmp.meta
    assert info == tmp.band_info

    tmp = arr + tmp_arr
    assert np.array_equal(2 * arr, tmp)
    assert num_ch == tmp.num_channels
    assert meta == tmp.meta
    assert info == tmp.band_info

    return


def test_get_rgb():
    """Test RGB conversion on multiple arrays."""

    # For 1,2,3 number of color channels, just return self
    for num_ch in [1, 2, 3]:
        arr = np.random.rand(10, 10, num_ch).astype(np.float32)
        tmp = SpectralArray(arr)
        rgb = tmp.get_rgb()
        assert np.array_equal(arr, tmp)

    # For more color channels, convert to RGB
    num_ch = 100

    # 1D Spectrum
    arr = np.random.rand(num_ch).astype(np.float32)
    tmp = SpectralArray(arr)
    rgb = tmp.get_rgb()
    assert rgb.shape == (3,)

    # 3D Spectrum
    arr = np.random.rand(10, 20, num_ch).astype(np.float32)
    tmp = SpectralArray(arr)
    rgb = tmp.get_rgb()
    assert rgb.shape == (10, 20, 3)

    # 4D Spectrum
    arr = np.random.rand(10, 20, 30, num_ch).astype(np.float32)
    tmp = SpectralArray(arr)
    rgb = tmp.get_rgb()
    assert rgb.shape == (10, 20, 30, 3)

    # 5D Spectrum
    arr = np.random.rand(10, 20, 30, 40, num_ch).astype(np.float32)
    tmp = SpectralArray(arr)
    rgb = tmp.get_rgb()
    assert rgb.shape == (10, 20, 30, 40, 3)

    return


def test_get_rgb_image():
    """Test conversion of true RGB from multispectral image"""
    testing.needs_internet()

    hsi_file = testing.get_remote_file(TEST_HSI_FILENAME)
    hsi = SpectralArray(np.load(hsi_file), dtype=np.float32)

    rgb_file = testing.get_remote_file(TEST_RGB_FILENAME)
    rgb = (imageio.imread(rgb_file) / 255.0).astype(np.float64)

    grey_file = testing.get_remote_file(TEST_GREY_FILENAME)
    grey = (imageio.imread(grey_file) / 255.0).astype(np.float64)[..., np.newaxis]

    assert np.allclose(rgb, hsi.get_rgb(), atol=0.01)

    # Test 1D real spectrum conversion
    for x, y in zip([0, 10, 20], [10, 100, 200]):
        spectrum = hsi[x, y, :]
        rgb_point = rgb[x, y, :]
        assert np.allclose(rgb_point, spectrum.get_rgb(), atol=0.01)

    # Calculate black and white from rgb
    grey_from_hsi = hsi.get_grey(weighted=True)
    grey_from_rgb = SpectralArray(rgb, dtype=np.float32).get_grey(weighted=True)
    grey_from_grey = SpectralArray(grey, dtype=np.float32).get_grey(weighted=True)

    assert np.allclose(grey, grey_from_grey, atol=0.01)
    assert np.allclose(grey, grey_from_rgb, atol=0.01)
    assert np.allclose(grey, grey_from_hsi, atol=0.01)

    return


def test_dimension_error():

    x = np.random.rand(5, 5, 3).astype(np.float32)

    # If ndim match, do not raise exception
    assert type(SpectralArray(x, ndim_exp=3, dtype=np.float32, copy=True)) == SpectralArray

    # If they do not match, throw DimensionError
    for ndim in [1, 2, 4, 5, 7, 11]:
        with raises(DimensionError) as cm:
            tmp_arr = SpectralArray(x, ndim_exp=ndim,
                                    dtype=np.float32, copy=False)

        assert f"Expected {ndim}D input. Found 3D." == str(cm.value)
