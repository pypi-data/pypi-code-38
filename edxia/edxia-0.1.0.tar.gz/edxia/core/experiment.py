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

"""A container class representing a mapping experiment"""

from ..utils import path
from ..io import raw_io

class MappingExperiment:
    _exp_number=0 # variable for automatic labelling of experiments

    """Contains information about a mapping experiment."""
    def __init__(self, pattern, label=None, description=None, map_format=None, bse_format=None):
        """

        :param pattern: the pattern of the file paths
        :param description: description
        """
        self._pattern = pattern
        if description is None:
            description = ""
        if label is None:
            label = str(MappingExperiment._exp_number)
            MappingExperiment._exp_number += 1
        if map_format is None:
            map_format=raw_io.esprit_ascii_map_format
        if bse_format is None:
            bse_format=raw_io.esprit_ascii_bse_format
        self._label = label
        self._description = description
        self._map_format = map_format
        self._bse_format = bse_format

        self._list_components = path.find_components(pattern)
        if len(self._list_components) == 0:
            raise RuntimeError("No components found for pattern '{0}'".format(pattern))

    @property
    def pattern(self):
        """Return the filepath pattern."""
        return self._pattern

    @property
    def label(self):
        """Return the label of the experiment."""
        return self._label

    @property
    def list_components(self):
        """Return the list of components available."""
        return self._list_components

    @property
    def map_format(self):
        """Return the format of the raw EDS map"""
        return self._map_format

    @property
    def bse_format(self):
        """Return the format of the raw BSE map"""
        return self._bse_format

    def get_path_map(self, component):
        """Return the path to the map of 'component'."""
        if component not in self._list_components:
            raise RuntimeError("'{0}' is not a valid component.".format(component))
        return path.find_component_path(self._pattern, component)


    def load_raw_map(self, component):
        """Load the map for a component.

        This is a low-level function, a loader should be used in normal operations"""
        if component == "BSE":
            return raw_io.load_txt_map(self.get_path_map(component), self.bse_format)
        else:
            return raw_io.load_txt_map(self.get_path_map(component), self.map_format)

class PartOfExperiment:
    """Base class for a subset of an experiment"""
    def __init__(self, parent=None):
        self._parent = parent

    @property
    def parent(self):
        return self._parent