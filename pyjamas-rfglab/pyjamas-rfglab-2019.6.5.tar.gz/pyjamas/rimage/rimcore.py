"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import Tuple

import matplotlib
matplotlib.use('Qt5Agg')  # https://stackoverflow.com/questions/21784641/installation-issue-with-matplotlib-python
import matplotlib.pyplot as plt
import numpy
from scipy.sparse.csgraph import dijkstra
from scipy.misc import toimage

from pyjamas.rimage.rimutils import rimutils


# SHOULD THIS BE CALLED RImageOps and all methods be static (similar to PIL.ImageOps)
class rimage:
    """
    A class to do image operations.

    The image is stored as a numpy array (image_array).

    Because numpy arrays are accessed by row and col, all methods implemented here will use the row, col convention even to
    represent points.
    """

    image_extensions: Tuple[str] = ('.tif', '.tiff', '.jpg')

    def __init__(self, image_in):
        self.image_array:numpy.array = image_in

    # Return a tuple with all the points between thesrc and thedst. thesrc and thedst are in (col=x, row=y) format
    def livewire(self, thesrc, thedst, margin):
        # Copy parameters. This is critical. I had a headache, because the function was modifying the parameter values.
        src = thesrc.copy()
        dst = thedst.copy()

        # Crop image. Note that image_array.shape returns size in (rows, columns) format. But src and dst are in (col=x, row=y) format.
        minx = max(0, min(src[0], dst[0]) - margin)
        maxx = min(self.image_array.shape[1] - 1, max(src[0], dst[0]) + margin) + 1
        miny = max(0, min(src[1], dst[1]) - margin)
        maxy = min(self.image_array.shape[0] - 1, max(src[1], dst[1]) + margin) + 1

        # Crop image.
        if self.image_array.ndim == 3:
            im = self.image_array[miny:maxy, minx:maxx, 0].copy()
        else:
            im = self.image_array[miny:maxy, minx:maxx].copy()

        # Adjust source and destination coordinates.
        src[0] -= minx
        src[1] -= miny
        dst[0] -= minx
        dst[1] -= miny

        src_ind, dst_ind = rimutils.sub2ind(im.shape, numpy.array([src[1], dst[1]]), numpy.array([src[0], dst[0]]))

        # Make sure the cropped image is a matrix and invert it so that high intensities become low ones, and we can
        # search for the minimal cost path.
        im[:] = numpy.max(im) - im[:]  # This modifies the array in place, which avoids having to reallocate the memory
        # (which is slow).
        # Doing im = numpy.max(im) - im produces the same result, but reallocates the memory.

        # Create graph.
        matrix_sparse, _ = rimutils.makeGraph(im)

        distances, predecessors = dijkstra(matrix_sparse, directed=True, indices=src_ind, return_predecessors=True)

        path = []

        i = dst_ind
        while i != src_ind:
            path.append(i)
            i = predecessors[i]

        path.append(src_ind)
        path = path[::-1]

        path = rimutils.ind2sub(im.shape, numpy.array(path))

        # Generate coordinates.
        return [[x+minx, y+miny] for x, y in zip(path[:][1], path[:][0])]

    def stretch(self, low: int = 0, high: int = 100, minimum: int = 0, maximum: int = 255) -> numpy.ndarray:
        """
        Linear stretch of the contrast of an image.
        :param low: lower percentile of the image to be mapped to the minimum value (0)
        :param high: higher percentile (100)
        :param minimum: minimum pixel value in the resulting image (0)
        :param maximum: maximum pixel value (255)
        :return: image_out, an image array.

        Has a sister method in rimutils.
        """

        image_out: numpy.array = []

        if high == low:
            return self.image_array

        if low > high:
            high, low = low, high

        # Define output variable.
        image_out = self.image_array

        # Find the appropriate pixel values for the low and high thresholds.
        if low == 0:
            low = numpy.min(self.image_array)
        else:
            low = numpy.percentile(self.image_array, low)

        if high == 100:
            high = numpy.max(self.image_array)
        else:
            high = numpy.percentile(self.image_array, high)

        # Determine the scaling factor.
        sc = (maximum - minimum) / (high - low)

        # Linear stretch of image_in.
        if low != 0:
            image_out = image_out - low

        if sc != 1:
            image_out = image_out * sc

        if minimum != 0:
            image_out = image_out + minimum

        return image_out

    def show(self):
        plt.imshow(toimage(self.image_array))
        plt.show()

        return