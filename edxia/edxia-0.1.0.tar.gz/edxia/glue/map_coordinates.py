# Copyright (c) 2019 Fabien Georget <fabien.georget@epfl.ch>, EPFL
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from glue.core.coordinates import Coordinates
import numpy as np
from astropy.wcs import WCS

class MatrixCoordinates(Coordinates):
    """A world coordinate system using a matrix transform.

    from https://github.com/glue-viz/glue-geospatial/blob/master/glue_geospatial/coordinates.py#L128

    Until it is implemented by default in glue"""
    def __init__(self, matrix, axis_labels):
        self.matrix = np.array(matrix)
        self.matrix_invert = np.linalg.inv(matrix)
        self.axis_labels = axis_labels

    def axis_label(self, axis):
        return self.axis_labels[axis]

    def pixel2world(self, *args):
        args = np.broadcast_arrays(*(args + ([1],)))
        shape_orig = args[0].shape
        args = [arg.ravel() for arg in args]
        result = np.matmul(self.matrix, args)[:-1]
        return [arg.reshape(shape_orig) for arg in result]

    def world2pixel(self, *args):
        args = np.broadcast_arrays(*(args + ([1],)))
        shape_orig = args[0].shape
        args = [arg.ravel() for arg in args]
        result = np.matmul(self.matrix_invert, args)[:-1]
        return [arg.reshape(shape_orig) for arg in result]

    @property
    def wcs(self):
        # We provide a wcs property since this can then be used by glue to
        # display world coordinates. In this case, the transformation matrix is
        # in the same order as the WCS convention so we don't need to swap
        # anything.
        wcs = WCS(naxis=self.matrix.shape[0] - 1)
        wcs.wcs.cd = self.matrix[:-1, :-1]
        wcs.wcs.crpix = np.zeros(wcs.naxis)
        wcs.wcs.crval = self.matrix[:-1, -1]
        wcs.wcs.ctype = self.axis_labels[::-1]
        return wcs

class MapCoordinates(MatrixCoordinates):
    """Coordinates for the map in real world"""
    def __init__(self, scale, row_trans=0, col_trans=0, labels=None):
        """
        :param scale: the scale factor
        :param row_trans: translation to apply to the rows
        :param col_trans: translation to apply to the columns
        :param labels: sequence of axis labels

        """
        if labels is None:
            labels = ("y", "x")

        self._scale = scale
        self._row_trans = row_trans
        self._col_trans = col_trans

        matrix=np.array([[scale, 0.0, scale*col_trans],[0.0, scale, scale*row_trans],[0.0, 0.0, 1.0]])
        super().__init__(matrix, labels)

    def world_axis_unit(self, axis):
        return "um"

    def __gluestate__(self, context):
        return dict(scale=self._scale, row_trans=self._row_trans, col_trans=self._col_trans, labels=self.axis_labels)

    @classmethod
    def __setgluestate__(cls, rec, context):
        return cls(scale=rec['scale'], row_trans=rec['row_trans'], col_trans=rec['col_trans'], labels=rec['labels'])
