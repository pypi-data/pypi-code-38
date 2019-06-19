# Copyright (c) 2015, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os.path
import PySide.QtGui as QtGui
from . import decorators

SIZE = 36
EMPTY_ICON = QtGui.QIcon()


class SvgIcon(object):
    blank = None
    data = 'data3.svg'
    chat = 'chat51.svg'
    graph = 'ascending7.svg'
    plot = 'graph.svg'
    coordinates = '3d76.svg'
    projection = 'textile.svg'
    plug = 'energy7.svg'
    x_axis = 'xaxis.svg'
    y_axis = 'yaxis.svg'
    z_axis = 'zaxis.svg'
    n_axis = 'naxis.svg'
    width = 'width3.svg'
    height = 'height6.svg'
    layers = 'layers.svg'
    layer = 'layer.svg'
    link = 'link5.svg'
    view = 'personal5.svg'
    ruler = 'ruler.svg'
    scales = 'scales2.svg'
    triangle = 'set1.svg'
    layout = 'layout.svg'
    text = 'label.svg'
    config = 'three115.svg'
    label = 'tag31.svg'
    list = 'list23.svg'
    pages = 'copy9.svg'
    page = 'page.svg'
    grid = 'squares8.svg'
    plus = 'add133.svg'
    minus = 'minus75.svg'
    picture = 'image.svg'
    # Icons for layers:
    scatter = 'scatter.svg'
    bar = 'barchart.svg'
    histogram1d = 'histogram.svg'
    histogram2d = 'hist2d.svg'
    line = 'linechart.svg'
    vlines = 'vlinechart.svg'
    bind = 'link5.svg'


@decorators.memoize
def create_icon(icon_name):
    """
    Create icon given its name.
    :param icon_name: Given from the Icons-class.
    :return: QIcon.
    """
    if icon_name is None:
        return EMPTY_ICON
    filename = '{}/svg_icons/{}'.format(
        os.path.dirname(__file__), icon_name)
    return QtGui.QIcon(filename)
