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


from abc import ABC, abstractmethod
from ...composite import CompositeMap
from ...core.map import MapsStack
from ...filters.scalers import ManualScaler
import numpy as np

class AbstractLoader(ABC):
    """Interface for a map loader"""
    def __init__(self, exp_manager, filters=None):

        self._exp_manager = exp_manager
        if filters is None:
            filters = []
        self._filters = filters

    @property
    def exp_manager(self):
        return self._exp_manager

    def get_path_map(self, component):
        """Return the path to a component map."""
        return self._exp_manager.get_path_map(component)

    @property
    def filters(self):
        """Return the list of filters to apply at loading."""
        return self._filters
    @filters.setter
    def filters(self, filters):
        """Set the list of filters to apply at loading."""
        self.reset_filters(filters)

    def add_filter(self, afilter):
        """Add a filter to the list of filters to apply at loading."""
        self._filters.append(afilter)
        self.reset_filters(self._filters)

    def reset_filters(self, filters):
        """Reset the list of filters."""
        self._filters = filters

    @abstractmethod
    def load_edsmap(component):
        """Load the map of 'component'."""
        pass

    def load_composite(self, channels):
        """Load a composite map."""
        maps = []
        for color in ["red", "green", "blue", "gray"]:
            if getattr(channels, color) is None:
                maps.append(None)
                continue

            tmap = self.load_edsmap(getattr(channels, color))
            # apply scaling after
            ManualScaler(getattr(channels, color+"_factor")).apply(tmap)
            maps.append(tmap)

        composite_img = None
        for i in range(3):
            if maps[i] is not None:
                if composite_img is None:
                    composite_img = np.zeros((maps[i].nb_rows, maps[i].nb_cols, 3))
                composite_img[:,:,i] = maps[i].map
        if maps[3] is not None:
            for i in range(3):
                composite_img[:,:,i] += maps[3].map/3
        return CompositeMap(composite_img, channels, self.exp_manager)


    def load_stack(self, components=None):
        if components is None:
            components = self.exp_manager.list_components
        if not hasattr(components, "__len__"):
            raise ValueError("Components must be a list of components")
        map0 = self.load_edsmap(components[0])
        stack = MapsStack(components, map0.shape, self.exp_manager)
        stack.set_map(map0)
        for i in range(1,len(components)):
            mapi = self.load_edsmap(components[i])
            stack.set_map(mapi)
        return stack
