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

"""Tests for plenpy.hyperspectral module.

"""

import os

import imageio
import numpy as np
from pytest import raises
import scipy.io


from plenpy import __name__ as APPNAME
from plenpy import testing
import plenpy.logg
from plenpy.spectral import SpectralImage
from plenpy.utilities.core import DimensionError


# Logging settings
logger = plenpy.logg.get_logger()
plenpy.logg.set_level("warning")

# Test data
TEST_HSI_FILENAME = "images/balloons.npy"
TEST_RGB_FILENAME = "images/balloons_RGB.png"
TEST_GREY_FILENAME = "images/balloons_GREY.png"
TEST_FILE_COLLECTION = "images/balloons/"

hsi_test_mono = np.random.rand(64, 64).astype(np.float32)
hsi_test_rgb = np.random.rand(64, 64, 3).astype(np.float32)
hsi_test_hyper = np.random.rand(64, 64, 30).astype(np.float32)


def test_spectral_image_new():
    """Test __new__"""

    for arr in [hsi_test_rgb, hsi_test_hyper]:

        tmp = SpectralImage(arr, dtype=np.float32, copy=True)
        assert np.array_equal(arr, tmp)

    # Wrong dimension
    arr = hsi_test_mono

    with raises(DimensionError) as cm:
        tmp = SpectralImage(arr, dtype=np.float32, copy=True)

    assert f"Expected 3D input. Found 2D." == str(cm.value)

    return


def test_from_file():
    """Test from_file() classmethod. Read RGB image."""

    testing.needs_internet()

    rgb_file = testing.get_remote_file(TEST_RGB_FILENAME)
    rgb = (imageio.imread(rgb_file) / 255.0).astype(np.float32)
    tmp = SpectralImage.from_file(rgb_file, format='PNG', dtype=np.float32)

    assert np.allclose(rgb, tmp)

    grey_file = testing.get_remote_file(TEST_GREY_FILENAME)
    grey = (imageio.imread(grey_file) / 255.0).astype(np.float32)

    assert grey.ndim == 2

    with raises(DimensionError) as cm:
        tmp = SpectralImage.from_file(grey_file, format='PNG', dtype=np.float32)

    assert f"Expected 3D input. Found 2D." == str(cm.value)

    return


def test_from_file_collection():
    testing.needs_internet()

    for i in range(1, 32):
        fname = TEST_FILE_COLLECTION + f"balloons_ms_{i:02d}.png"
        testing.get_remote_file(fname)

    # Read from file collection
    path = os.path.join(testing.appdata_dir(APPNAME), TEST_FILE_COLLECTION)
    tmp = SpectralImage.from_file_collection(path=path)

    hsi_file = testing.get_remote_file(TEST_HSI_FILENAME)
    hsi = np.load(hsi_file)

    assert np.allclose(hsi, tmp)

    return


def test_from_mat():
    testing.needs_internet()

    # Get a temporary folder
    path, id = testing.get_tmp_folder()

    try:
        matname = "test_hsi.mat"
        path = os.path.join(path, matname)

        hsi_file = testing.get_remote_file(TEST_HSI_FILENAME)
        hsi = np.load(hsi_file)

        mdict = dict(data=hsi)
        scipy.io.savemat(path, mdict)

        # Try loading with and without key
        for key in [None, 'data']:
            tmp = SpectralImage.from_mat_file(path=path, key=key)

            assert np.allclose(hsi, tmp)

    finally:
        # Cleanup temporary folder
        testing.remove_tmp_folder(id)

    return


def test_save():
    # Get a temporary folder
    path, id = testing.get_tmp_folder()

    try:
        # Create example image
        arr = np.random.rand(64, 32, 30).astype(np.float32)

        tmp = SpectralImage(arr, dtype=np.float32, copy=False)

        for d in [np.uint8, np.uint16]:
            tmp.save(path=path, ext='.png', dtype=d)

            # Load image
            loaded = SpectralImage.from_file_collection(path=path,
                                                        dtype=np.float32)

            # Caution: lossy dtype conversion
            assert np.allclose(arr,  loaded, atol=0.01)

        # Test error handling
        with raises(ValueError) as cm:
            tmp.save(path=path, ext='.NONSENSE')

        assert f"Unknown extension .NONSENSE ." == str(cm.value)

    finally:
        # Cleanup temporary folder
        testing.remove_tmp_folder(id)

    return


def test_save_rgb():
    # Get a temporary folder
    path, id = testing.get_tmp_folder()

    try:
        # Create example image
        arr = np.random.rand(64, 32, 30).astype(np.float32)

        tmp = SpectralImage(arr, dtype=np.float32, copy=False)
        tmp_rgb = tmp.get_rgb()

        rgb_filename = os.path.join(path, "test_rgb_img.png")
        tmp.save_rgb(rgb_filename)

        # Load image
        loaded = SpectralImage.from_file(path=rgb_filename, dtype=np.float32)

        # Caution: lossy dtype conversion
        assert np.allclose(tmp_rgb, loaded, atol=0.01)

        # Test error handling
        rgb_filename = os.path.join(path, "test_rgb_img.NONSENSE")

        with raises(ValueError) as cm:
            tmp.save_rgb(rgb_filename)

        assert f"Unknown extension .NONSENSE ." == str(cm.value)

    finally:
        # Cleanup temporary folder
        testing.remove_tmp_folder(id)

    return
