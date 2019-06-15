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
from ..utils import coordinates
from .experiment import PartOfExperiment
from ..utils.chemistry import molar_masses, oxides

class Map(PartOfExperiment):
    """A 2D EDS Map"""
    def __init__(self, component, eds_map, parent):
        """
        :param component: the component
        :param eds_map: the map as a 2D numpy array
        :param parent: the experiment manager
        """
        super().__init__(parent=parent)
        self._component = component
        self._map = eds_map
        self._parent = parent

    @property
    def component(self):
        """The map component"""
        return self._component

    @property
    def map(self):
        """The map"""
        return self._map
    @map.setter
    def map(self, amap):
        """Set the map"""
        self._map = amap

    @property
    def shape(self):
        """The shape of the map"""
        return self._map.shape

    @property
    def nb_rows(self):
        """The number of rows"""
        return self._map.shape[0]

    @property
    def nb_cols(self):
        """The number of columns"""
        return self._map.shape[1]

    def __getitem__(self, key):
        """Access the map (as you would access the numpy array)"""
        return self._map[key]

    def rc(self, r, c):
        """Return the value of the map in the rc coordinates system."""
        return self.map[r, c]

    def xy(self, x, y):
        """Return the value of the map in the xy coordinates system."""
        r, c = coordinates.xy_to_rc(self._map, x, y)
        return self.map[r,c]

    @property
    def flat_map(self):
        """Return the map as a 1D array."""
        return self._map.reshape((self.nb_rows*self.nb_cols))

    def copy_without_map(self):
        return Map(self.component, None, self.parent)

class MapsStack(PartOfExperiment):
    """A stack of maps"""
    def __init__(self, components, shape, parent):
        """
        :param components: the list of components
        :param shape: the shape of a map (nb_rows, nb_cols)
        :param parent: the experiment manager
        """
        super().__init__(parent)
        self._components = components
        self._maps = np.zeros((shape[0], shape[1], len(components)))

    @property
    def shape(self):
        """Return the shape of the maps array."""
        return self._maps.shape

    @property
    def maps(self):
        """Returns the numpy array containing the maps"""
        return self._maps

    @property
    def components(self):
        """Returns the list of components."""
        return self._components

    def index(self, component):
        """Returns the index of the component."""
        return self._components.index(component)

    def __getitem__(self, args):
        """Returns values from the maps, args is a numpy index/slice."""
        return self._maps[args]

    def map(self, component):
        """Return the map for a component."""
        return Map(component, self._maps[:,:,self.index(component)], self.parent)

    def set_map(self, amap):
        idx = self.index(amap.component)
        self._maps[:,:,idx] = amap.map

    def composition(self, r, c):
        """Return the composition at a point"""
        return dict(zip(self.components, self._maps[r,c,:]))

    def to_atomic(self, copy=True):
        """Transform the maps to atomic"""
        if copy:
            maps = self._maps.copy()
        else:
            maps = self._maps
        for ind, component in enumerate(self._components):
            if component == "BSE":
                continue
            maps[:,:,ind] /= molar_masses[component]
            tot_at = maps.sum(axis=2)
        for ind, component in enumerate(self._components):
            if component == "BSE":
                continue
            maps[:,:,ind] *= 1.0/tot_at
        if copy:
            shape = self._maps.shape
            stack = MapsStack(self._components, (shape[0], shape[1]), self.parent)
            stack._maps = maps
            return stack
        else:
            return self

    def normalize(self, copy=True):
        """Normalize the EDS maps, so their sum at each point is 1."""
        if copy:
            maps = self._maps.copy()
        else:
            maps = self._maps
        if "BSE" in self.components:
            maps = maps/((maps.sum(axis=2)-self.map("BSE").map)[:,:,  np.newaxis])
        else:
            maps = maps/(maps.sum(axis=2)[:,:,  np.newaxis])
        if copy:
            shape = self._maps.shape
            stack = MapsStack(self._components, (shape[0], shape[1]), self.parent)
            stack._maps = maps
            return stack
        else:
            return self

    def sum_of_oxides_from_mass(self):
        """Compute the sum of oxides from a mass map."""
        s_oxide = np.zeros((self.shape[0], self.shape[1]))
        for ind, elem in enumerate(self.components):
            if elem in oxides.keys():
                s_oxide += self._maps[:,:,ind]*molar_masses[oxides[elem][0]]/(oxides[elem][1]*molar_masses[elem])
        return s_oxide