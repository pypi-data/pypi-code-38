#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2016-2018 Cyril Desjouy <cyril.desjouy@univ-lemans.fr>
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
# Creation Date : mer. 9 avril 2015 10:30:45 CEST
"""
-----------
DOCSTRING

@author: Cyril Desjouy
"""

import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import math
import copy


__all__ = ['modified_jet', 'grayify_cmap',
           'cmap_center_point_adjust', 'MidpointNormalize']


def modified_jet():
    """
    Modified jet colormap
    howto : http://matplotlib.org/examples/pylab_examples/custom_cmap.html
    """
    from matplotlib.colors import LinearSegmentedColormap
    cdictjet = {'blue': ((0.0, 1., 1.),
                         (0.11, 1, 1),
                         (0.34, 1, 1),
                         (0.48, 1, 1),
                         (0.52, 1, 1),
                         (0.65, 0, 0),
                         (1, 0, 0)),
                'green': ((0.0, 0.6, 0.6),
                          (0.125, 0.8, 0.8),
                          (0.375, 1, 1),
                          (0.48, 1, 1),
                          (0.52, 1, 1),
                          (0.64, 1, 1),
                          (0.91, 0, 0),
                          (1, 0, 0)),
                'red': ((0.0, 0, 0),
                        (0.35, 0, 0),
                        (0.48, 1, 1),
                        (0.52, 1, 1),
                        (0.66, 1, 1),
                        (0.8, 1, 1),
                        (1, 0., 0.))
                }
    cmc = LinearSegmentedColormap('mjet', cdictjet, 1024)
    plt.register_cmap(cmap=cmc)

    return cmc


def grayify_cmap(cmap):
    """Return a grayscale version of the colormap"""
    cmap = plt.cm.get_cmap(cmap)
    colors = cmap(np.arange(cmap.N))

    # convert RGBA to perceived greyscale luminance
    # cf. http://alienryderflex.com/hsp.html
    RGB_weight = [0.299, 0.587, 0.114]
    luminance = np.sqrt(np.dot(colors[:, :3] ** 2, RGB_weight))
    colors[:, :3] = luminance[:, np.newaxis]

    return cmap.from_list(cmap.name + "_grayscale", colors, cmap.N)


def _cmap_powerlaw_adjust(cmap, a):
    '''
    returns a new colormap based on the one given
    but adjusted via power-law:

    newcmap = oldcmap**a
    '''
    if a < 0.:
        return cmap
    cdict = copy.copy(cmap._segmentdata)
    fn = lambda x: (x[0]**a, x[1], x[2])
    for key in ('red', 'green', 'blue'):
        cdict[key] = map(fn, cdict[key])
        cdict[key].sort()
        assert (cdict[key][0] < 0 or cdict[key][-1] > 1), \
            "Resulting indices extend out of the [0, 1] segment."
    return colors.LinearSegmentedColormap('colormap', cdict, 1024)


def _cmap_center_adjust(cmap, center_ratio):
    '''
    [ ONLY WITH PYTHON 2.X]

    returns a new colormap based on the one given
    but adjusted so that the old center point higher
    (>0.5) or lower (<0.5)
    '''
    if not (0. < center_ratio) & (center_ratio < 1.):
        return cmap
    a = math.log(center_ratio) / math.log(0.5)
    return _cmap_powerlaw_adjust(cmap, a)


def cmap_center_point_adjust(cmap, range, center):
    '''
    [ ONLY WITH PYTHON 2.X]

    converts center to a ratio between 0 and 1 of the
    range given and calls cmap_center_adjust(). returns
    a new adjusted colormap accordingly
    '''
    if not ((range[0] < center) and (center < range[1])):
        return cmap
    return _cmap_center_adjust(cmap, abs(center - range[0]) / abs(range[1] - range[0]))


class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):

        if self.vmin < self.midpoint < self.vmax:
            x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
            return np.ma.masked_array(np.interp(value, x, y))

        else:
            x, y = [self.vmin, (self.vmax+self.vmin)/2, self.vmax], [0, 0.5, 1]
            return np.ma.masked_array(np.interp(value, x, y))

