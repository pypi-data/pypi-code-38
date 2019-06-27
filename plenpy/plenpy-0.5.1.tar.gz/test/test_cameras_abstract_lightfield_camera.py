# Copyright (C) 2018  The Plenpy Authors
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


"""Tests for plenpy.cameras.abstract_lightfield_camera module.

"""

import os
from unittest.mock import patch

import numpy as np
from imageio import imread, imsave
from pytest import raises

import plenpy.logg

from plenpy import __name__ as APPNAME
from plenpy import testing
from plenpy.cameras.abstract_lightfield_camera import AbstractLightFieldCamera

# Logging settings
logger = plenpy.logg.get_logger()
plenpy.logg.set_level("warning")

APP_FOLDER = testing.appdata_dir(APPNAME)

# Global test names
TEST_IMG_FILENAME = "images/crayons.jpeg"
BASE_FOLDERPATH = os.path.abspath(APP_FOLDER)
CAMERA_FOLDERPATH = os.path.join(BASE_FOLDERPATH, "test_camera/")
IMAGES_FOLDERPATH = os.path.join(CAMERA_FOLDERPATH, "Images/")
CALIBRATION_FOLDERPATH = os.path.join(CAMERA_FOLDERPATH, "Calibration/")

FILES = [os.path.join(IMAGES_FOLDERPATH, "img_1.png"),
         os.path.join(CALIBRATION_FOLDERPATH, "img_cal_1.png"),
         os.path.join(CALIBRATION_FOLDERPATH, "img_cal_2.png"),
         os.path.join(CALIBRATION_FOLDERPATH, "cal_data.npz"),
         os.path.join(CALIBRATION_FOLDERPATH, "myfile.npz")]


FOLDERS = [BASE_FOLDERPATH,
           CAMERA_FOLDERPATH,
           CALIBRATION_FOLDERPATH,
           IMAGES_FOLDERPATH]

# Create Mock Patch Abstract Base Classes
ABC_PATCH = patch.multiple(AbstractLightFieldCamera, __abstractmethods__=set())


# Create a test camera
def create_test_lf_camera():
    """ Helper function to create a test lightfield camera folder structure
    with images and calibration whiteimages.
    """

    # Create folder structure
    for folder in FOLDERS:
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass

    img_file = testing.get_remote_file(TEST_IMG_FILENAME)
    img = imread(img_file)

    # Save test image
    imsave(FILES[0], img)

    # Create greyscale whiteimages
    whiteimg_1 = (255 * np.ones((img.shape[0], img.shape[1]))).astype(np.uint8)
    whiteimg_2 = (127 * np.ones((img.shape[0], img.shape[1]))).astype(np.uint8)

    # Save whiteimages
    imsave(FILES[1], whiteimg_1)
    imsave(FILES[2], whiteimg_2)

    del img
    return


def delete_test_lf_camera():
    """ Helper function to delete the test camera created by
    :func:`create_test_camera()`.
    """
    for file in FILES:
        try:
            os.unlink(file)
        except FileNotFoundError:
            pass

    for folder in reversed(FOLDERS):
        try:
            if not folder == BASE_FOLDERPATH:
                os.rmdir(folder)
        except FileNotFoundError:
            pass

    return


def test_abstract_lightfield_camera_init():

    try:
        # Create camera folder structure
        create_test_lf_camera()

        # Create a mock patch to test abstract base class
        ABC_PATCH.start()
        test_camera = AbstractLightFieldCamera(CAMERA_FOLDERPATH,
                                               microlens_size=10,
                                               grid_type='hex')

        # Check member variables
        assert test_camera._microlensSize == 10
        assert test_camera._microlensRadius == 5
        assert test_camera._gridType == 'hex'
        assert test_camera._microlensFocalLength is None
        assert test_camera._calibrationDB is None
        assert test_camera._whiteImageDB is None
        assert test_camera._calDataFilename == os.path.join(
            CALIBRATION_FOLDERPATH, 'cal_data.npz')

        # Check microlens radius rounding
        test_camera = AbstractLightFieldCamera(CAMERA_FOLDERPATH,
                                               microlens_size=9,
                                               grid_type='hex')
        assert test_camera._microlensRadius == 4

        # Test error handling
        with raises(ValueError) as cm:
            test_camera = AbstractLightFieldCamera(CAMERA_FOLDERPATH,
                                                   microlens_size=9,
                                                   grid_type='nonsense')

        assert ("Unknown grid type 'nonsense'. "
                "Valid types are 'hex' and 'rect'.") == str(cm.value)

        ABC_PATCH.stop()

    finally:
        # Always clean up
        delete_test_lf_camera()

    return


def test_abstract_lightfield_camera_save_load_caldata():

    try:
        # Create camera folder structure
        create_test_lf_camera()

        # Create a mock patch to test abstract base class
        ABC_PATCH.start()
        test_camera = AbstractLightFieldCamera(CAMERA_FOLDERPATH,
                                               microlens_size=10,
                                               grid_type='hex')

        # Set test members
        test_wi_db = dict(test1='test', test2=1234)
        test_cal_db = dict(test1='test_calibration', test2=3.87235)
        test_camera._whiteImageDB = test_wi_db
        test_camera._calibrationDB = test_cal_db

        # Save data, reset and load
        test_camera._save_cal_data()
        test_camera._whiteImageDB = None
        test_camera._calibrationDB = None
        test_camera._load_cal_data()

        assert test_camera._whiteImageDB == test_wi_db
        assert test_camera._calibrationDB == test_cal_db

        # Save data, reset and load
        test_camera._save_cal_data(filename="myfile.npz")
        test_camera._whiteImageDB = None
        test_camera._calibrationDB = None
        test_camera._load_cal_data(filename="myfile.npz")

        assert test_camera._whiteImageDB == test_wi_db
        assert test_camera._calibrationDB == test_cal_db

        ABC_PATCH.stop()

    finally:
        # Always clean up
        delete_test_lf_camera()
    return
