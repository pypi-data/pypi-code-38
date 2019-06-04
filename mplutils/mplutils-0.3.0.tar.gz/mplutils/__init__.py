#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2016-2019 Cyril Desjouy <cyril.desjouy@univ-lemans.fr>
#
# This file is part of mplutils
#
# mplutils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mplutils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mplutils. If not, see <http://www.gnu.org/licenses/>.
#
#
# Creation Date : mer. 11 avril 2018 21:39:33 CEST
"""
-----------
DOCSTRING

@author: Cyril Desjouy
"""

from .custom_cmap import modified_jet, grayify_cmap, cmap_center_point_adjust, MidpointNormalize
from .multi_pcolor import set_figsize, get_subplot_shape

__version__ = "0.3.0"
