#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2016-2019 Cyril Desjouy <cyril.desjouy@univ-lemans.fr>
#
# This file is part of {name}
#
# {name} is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# {name} is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with {name}. If not, see <http://www.gnu.org/licenses/>.
#
# Creation Date : 2019-06-03 - 21:31:43
"""
-----------
DOCSTRING

@author: Cyril Desjouy
"""


import tkinter
import numpy as np


def get_subplot_shape(n):
    """ Get best arangment with n subplots, n being between 1 and 12."""

    if n == 1:
        return 1, 1

    if 2 <= n <= 12:
        if n%2 != 0 and n%3 != 0:
            n += 1

        dim1 = max([i for i in range(1, 6) if n%i == 0 and n != i])
        dim2 = int(n/dim1)

        if dim1 > dim2:
            return dim2, dim1
        if dim1 <= dim2:
            return dim1, dim2

    raise ValueError('Wrong number of subplots (1<=n<=12)')


def get_screen_xy(metric='inch', xbound=None, ybound=None):
    """ Get screen dimensions.

    Parameters
    ----------
    metric : must be 'inch', 'mm', or 'px'.
    xbound, ybound : max resolution to consider. Useful with multiple screens.
    """

    root = tkinter.Tk()

    mm_per_inch = 25.4
    # dpi (pixels per inch ~ 96 classically) :
    dpi = root.winfo_screenheight()/root.winfo_screenmmheight()*mm_per_inch

    if xbound is not None:
        width = min(root.winfo_screenwidth(), xbound)
    else:
        width = root.winfo_screenwidth()

    if ybound is not None:
        height = min(root.winfo_screenheight(), ybound)
    else:
        height = root.winfo_screenheight()

    root.destroy()

    if metric == 'inch':
        return width/dpi, height/dpi

    if metric == 'mm':
        return width/dpi*mm_per_inch, height/dpi*mm_per_inch

    if metric == 'px':
        return width, height

    raise ValueError("metric must be 'inch', 'mm', or 'px'")


def set_figsize(axes, figsize, size=70):
    """ Returns ideal figsize.

    Parameters
    ----------

    axes : axes of the figure to consider
    figsize : can be a tuple or 'auto' (str).
    size : size of the figure in percent of the screen. int
    """

    if figsize == 'auto':

        width, height = get_screen_xy(xbound=1920, ybound=1080)
        width, height = width*size/100, height*size/100

        if isinstance(axes, np.ndarray):
            rows, columns = get_subplot_shape(axes.size)
            y = axes.ravel()[0].get_ybound()
            x = axes.ravel()[0].get_xbound()
            ratio = rows*(y[1]-y[0])/(columns*(x[1]-x[0]))
        else:
            ratio = axes.get_data_ratio()

        if width*ratio > height:
            figsize = 1.5*height/ratio, height
        else:
            figsize = width, width*ratio*1.2

    return figsize
