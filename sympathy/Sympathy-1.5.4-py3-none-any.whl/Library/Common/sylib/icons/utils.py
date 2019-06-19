# Copyright (c) 2016, Combine Control Systems AB
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

from matplotlib import colors as mpl_colors

from sylib.figure import colors
from sylib.report import decorators

from PySide import QtGui


SIZE = 26
EMPTY_ICON = QtGui.QIcon()


class SvgIcon(object):
    blank = None
    angle = 'angle.svg'
    arrow = 'arrow.svg'
    vert_align = 'vert_align.svg'
    horz_align = 'horz_align.svg'
    invalid = 'ban-circle-symbol.svg'
    data = 'data3.svg'
    chat = 'chat51.svg'
    graph = 'ascending7.svg'
    plot = 'view-plot-axes-symbolic.svg'
    coordinates = '3d76.svg'
    projection = 'textile.svg'
    percentage = 'percentage.svg'
    plug = 'energy7.svg'
    x_axis = 'view-xaxis-symbolic.svg'
    y_axis = 'view-yaxis-symbolic.svg'
    z_axis = 'view-zaxis-symbolic.svg'
    n_axis = 'view-naxis-symbolic.svg'
    x_axis_pos_bottom = 'view-xaxis-bottom-symbolic.svg'
    x_axis_pos_top = 'view-xaxis-top-symbolic.svg'
    y_axis_pos_left = 'view-yaxis-left-symbolic.svg'
    y_axis_pos_right = 'view-yaxis-right-symbolic.svg'
    axes_bottom_left = 'view-axes-bottom-left-symbolic.svg'
    axes_bottom_right = 'view-axes-bottom-right-symbolic.svg'
    axes_top_left = 'view-axes-top-left-symbolic.svg'
    axes_top_right = 'view-axes-top-right-symbolic.svg'
    x_data = 'x-data-symbolic.svg'
    y_data = 'y-data-symbolic.svg'
    z_data = 'z-data-symbolic.svg'
    width = 'width3.svg'
    height = 'height6.svg'
    rotate = 'rotate.svg'
    rounded_rectangle = 'rounded_rectangle.svg'
    layers = 'layers.svg'
    layer = 'layer.svg'
    link = 'link5.svg'
    view = 'personal5.svg'
    ruler = 'ruler.svg'
    scales = 'scales2.svg'
    triangle = 'set1.svg'
    layout = 'layout.svg'
    text = 'label.svg'
    text_size = 'text-size.svg'
    location = 'location.svg'
    frame = 'frame-on-off.svg'
    number_columns = 'number_columns.svg'
    aspect_ratio = 'view-plot-aspect-ratio-symbolic.svg'
    ticks = 'view-plot-axes-ticks.svg'
    config = 'three115.svg'
    label = 'tag31.svg'
    labels = 'labels.svg'
    aspect = 'view-aspect-symbolic.svg'
    color = 'view-color-symbolic.svg'
    alpha = 'view-alpha-symbolic.svg'
    linewidth = 'view-linewidth-symbolic.svg'
    linestyle = 'view-linestyle-symbolic.svg'
    drawstyle = 'view-drawstyle-symbolic.svg'
    hatch_pattern = 'hatch-pattern.svg'
    histtype = 'view-histtype-symbolic.svg'
    marker = 'view-marker-symbolic.svg'
    markersize = 'view-markersize-symbolic.svg'
    bin_min_edge = 'view-bin-min-edge-symbolic.svg'
    bin_max_edge = 'view-bin-max-edge-symbolic.svg'
    barwidth = 'view-bar-width-symbolic.svg'
    barlabelvalgin = 'view-valign-symbolic.svg'
    bar_grouping = 'view-grouping-symbolic.svg'
    colorbar_orientation = 'view-plot-colorbar-orientation-symbolic.svg'
    colorbar_min = 'view-plot-colorbar-min-symbolic.svg'
    colorbar_max = 'view-plot-colorbar-max-symbolic.svg'
    limit = 'view-limit-symbolic.svg'
    list = 'list23.svg'
    pages = 'copy9.svg'
    page = 'page.svg'
    grid = 'view-plot-grid-symbolic.svg'
    legend = 'view-plot-legend-symbolic.svg'
    visible = 'eye-open.svg'
    invisible = (
        'eye-with-a-diagonal-line-interface-symbol-for-invisibility.svg')
    plus = 'add133.svg'
    minus = 'minus75.svg'
    picture = 'image.svg'
    show_frame = 'view-plot-frame-visibility.svg'
    boxplot = 'boxplot.svg'
    piechart = 'piechart.svg'
    piechart_explode = 'piechart_explode.svg'
    piechart_shadow = 'piechart_shadow.svg'
    diameter = 'diameter.svg'
    errorbar = 'errorbar.svg'
    ypos = 'ypos.svg'
    timeline = 'timeline.svg'
    imageplot = 'imageplot.svg'
    # Icons for layers:
    scatter = 'view-plot-scatter-symbolic.svg'
    bar = 'view-plot-bar-symbolic.svg'
    histogram1d = 'view-plot-hist-symbolic.svg'
    heatmap = 'view-plot-heatmap-symbolic.svg'
    line = 'view-plot-line-symbolic.svg'
    lines = 'view-plot-lines-symbolic.svg'
    barcontainer = 'view-plot-barcontainer-symbolic.svg'
    histcontainer = 'view-plot-histcontainer-symbolic.svg'
    iterator = 'view-plot-iterator-symbolic.svg'
    vlines = 'vlinechart.svg'
    bind = 'link5.svg'
    rectangles = 'rectangles.svg'
    ellipses = 'ellipses.svg'
    filled = 'filled.svg'
    # control icons:
    copy = 'copy9.svg'
    delete = 'edit-trash-symbolic.svg'
    # logic
    and_ = 'and.svg'
    or_ = 'or.svg'
    # query
    field = 'query-field.svg'
    arrayfield = 'query-arrayfield.svg'
    importquery = 'query-importquery.svg'


@decorators.memoize
def create_icon(icon_name):
    """
    Create icon given its name.
    :param icon_name: Given from the Icons-class.
    :return: QIcon.
    """
    if icon_name is None:
        return EMPTY_ICON

    if os.path.isabs(icon_name):
        filename = icon_name
    else:
        filename = '{}/svg_icons/{}'.format(
            os.path.dirname(__file__), icon_name)
    return QtGui.QIcon(filename)


@decorators.memoize
def color_icon(color):
    """
    Create filled icon with given color.
    Parameters
    ----------
    color : list or tuple or str or unicode

    Returns
    -------
    QIcon
    """
    color = colors.parse_to_mpl_color(color)
    if color is None:
        return create_icon(SvgIcon.color)
    rgbf_color = mpl_colors.colorConverter.to_rgb(color)
    qim = QtGui.QImage(SIZE, SIZE, QtGui.QImage.Format_ARGB32)
    qim.fill(QtGui.QColor.fromRgbF(*rgbf_color))
    pixmap = QtGui.QPixmap.fromImage(qim)
    return QtGui.QIcon(pixmap)


if __name__ == '__main__':
    app = QtGui.QApplication([])

    icon = color_icon('#fefe22')
    widget = QtGui.QPushButton()
    widget.setIcon(icon)
    widget.show()
    widget.raise_()

    app.exec_()
