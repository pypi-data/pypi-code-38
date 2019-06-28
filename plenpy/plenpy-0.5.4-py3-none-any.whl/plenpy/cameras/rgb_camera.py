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


"""
Module defining the :class:`RgbCamera` class.

"""
from typing import Optional

import matplotlib.pyplot as plt

import plenpy.logg

from plenpy.cameras.abstract_camera import AbstractCamera
from plenpy.utilities import demosaic
from plenpy.utilities import images

logger = plenpy.logg.get_logger()

__all__ = ['RgbCamera']


class RgbCamera(AbstractCamera):
    """Basic RGB camera.

    This class is a very basic camera class illustrating the implementation
    of the necessary class methods such as calibration and decoding.
    The RGB camera decoding process is in this case just a simple
    demosaicing of the raw sensor image.

    Todo:
    Implement the calibration of a camera model, e.g. to do rectification
    of the images.

    Attributes:
        _bayerPattern (str): The camera's mosaicing Bayer pattern.

    """

    def __init__(self, camera_folder_path: str,
                 bayer_pattern: str):
        """:class:`RgbCamera` class initialization.

        Args:
            camera_folder_path: System path to the main camera folder.

            bayer_pattern: The camera's mosaicing Bayer pattern.
                See also :func:`plenpy.utilities.demosaic.get_demosaiced()`.

        """
        logger.info("Initializing RGB camera.")
        # Call init from AbstractCamera base class
        super().__init__(camera_folder_path)
        self._bayerPattern = bayer_pattern

    def calibrate(self):
        # Could do calibration of a camera model here,
        # e.g. to do rectification etc.
        pass

    def decode_sensor_image(self,
                            num: int,
                            method: Optional[str] = None):
        """Decode the sensor image of the RGB Camera.

        This is just a demosaicing of
        the monochromatic sensor image to obtain a RGB color image.

        Args:
            num: Number of the sensor image to decode.

            method: Method used to calculate the demosaiced image.
                See Also :func:`.plenpy.utilities.demosaic.get_demosaiced()`

        """

        # Get sensor image
        img = self.get_sensor_image(num)

        # Do debayering of sensor image
        demosaiced = demosaic.get_demosaiced(img=img,
                                             method=method,
                                             pattern=self._bayerPattern)

        # Normalize to float valued image
        demosaiced = images.dtype_to_norm_float(demosaiced, img.dtype)

        # Add decoded image to _decodedImages dictionary
        self._add_decoded_image(demosaiced, num)
        return

    def show_decoded_image(self,
                           num: int,
                           plt_show: bool = True):
        """Show the decoded image using matplotlib.

        Args:
            num: Number of the sensor image that the image is decoded from.

            plt_show : Flag indicating whether to call
                :func:`.matplotlib.pyplot.show()` at the end.

        """
        plt.figure()
        plt.imshow(self.get_decoded_image(num))

        if plt_show is True:
            plt.show()

        return
