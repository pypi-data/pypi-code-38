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

import numpy as np

"""Raw format loaders

Example:
    Read txt format from bruker Esprit software
    >>> bse_map_asarray = load_txt_map("map234_BSE.txt", esprit_ascii_map_format)
"""

class TextMapFormat:
    """A struct-like class to contain formatting information about raw
    EDS maps.
    """
    def __init__(self, delimiter, min_value, max_value, saveformat="%.4f"):
        """

        :param delimiter: delimiter between cells
        :param max_value: maximum value possible
        :param min_value: minimum value possible
        :param saveformat: format used when saving a map
        """
        self._delimiter = delimiter
        self._max_value = max_value
        self._min_value = min_value
        self._saveformat = saveformat

    @property
    def delimiter(self):
        """Return the column delimiter"""
        return self._delimiter
    @delimiter.setter
    def delimiter(self, value):
        """Set the column delimiter"""
        self._delimiter = value

    @property
    def max_value(self):
        """Return the maximum value allowed in the map"""
        return self._max_value
    @max_value.setter
    def max_value(self, value):
        """Set the maximum value allowed in the map"""
        self._max_value = value

    @property
    def min_value(self):
        """Return the minimum value allowed in the map"""
        return self._min_value
    @min_value.setter
    def min_value(self, value):
        """Set the minimum value allowed in the map"""
        self._min_value = value

    @property
    def saveformat(self):
        """Set the save format"""
        return self._saveformat
    @saveformat.setter
    def saveformat(self, astring):
        """Set the save format"""
        self._saveformat = astring

    def copy(self):
        """Copy the format"""
        return TextMapFormat(self.delimiter, self.min_value, self.max_value, self.saveformat)

esprit_ascii_map_format = TextMapFormat(delimiter=";", min_value=0, max_value=100)
esprit_ascii_bse_format = TextMapFormat(delimiter=";", min_value=0, max_value=-1)


def load_txt_map(filename, txtformat):
    """Load a 2D map

    :param filename: filepath to the text map
    :param txtformat: the format of the text map
    :returns: a 2D numpy array normalized between [0,1]
    :raises: whatever numpy.loadtxt can raise
    """
    data = np.loadtxt(filename, delimiter=txtformat.delimiter, dtype=np.float)
    # normalize to [0,1]
    if txtformat.max_value==-1:
        data = (data-txtformat.min_value)/(data.max()-txtformat.min_value)
    else:
        data = (data-txtformat.min_value)/(txtformat.max_value-txtformat.min_value)
    return np.clip(data, 0.0, 1.0)

def save_txt_map(filename, amap, txtformat):
    """Save a 2D map

    Perform a copy first to normalize the data according the format.

    :param filename: filepath to the file
    :param amap: a 2D map
    :format txtformat: the format of the ascii saved map
    """
    data = amap.copy()
    data = data*(txtformat.max_value-txtformat.min_value)+txtformat.min_value
    np.savetxt(filename, data, delimiter=txtformat.delimiter, fmt=txtformat.saveformat)

def load_pickle_map(filepath):
    """Load a map that was previously saved as a pickle dump"""
    return np.load(filepath)


def save_pickle_map(filepath, data):
    """Dump a map in a binary format"""
    np.save(filepath, data)
