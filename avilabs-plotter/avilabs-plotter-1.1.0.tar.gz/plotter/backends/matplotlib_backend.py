from typing import List

import matplotlib.pyplot as plt

from ..backend import Backend
from ..color import Color, ColorMap
from ..enums import LegendLocation, LineStyle, Marker
from ..frame import Frame
from ..chart import Chart


class MatplotlibBackend(Backend):
    loc_map = {
        LegendLocation.BEST: 0,
        LegendLocation.UPPER_RIGHT: 1,
        LegendLocation.UPPER_LEFT: 2,
        LegendLocation.UPPER_CENTER: 9,
        LegendLocation.LOWER_RIGHT: 4,
        LegendLocation.LOWER_LEFT: 3,
        LegendLocation.LOWER_CENTER: 8
    }

    style_map = {
        LineStyle.SOLID: '-',
        LineStyle.DASH: '--',
        LineStyle.DASHDOT: '-.',
        LineStyle.DOT: ':'
    }

    marker_map = {
        Marker.POINT: '.',
        Marker.PIXEL: ',',
        Marker.STAR: '*',
        Marker.PLUS: '+',
        Marker.X: 'x',
        Marker.CIRCLE: 'o',
        Marker.TRIANGLE: '^',
        Marker.SQAURE: 's',
        Marker.PENTAGON: 'p',
        Marker.HEXAGON: 'h',
        Marker.DIAMOND: 'd',
        Marker.VLINE: '|',
        Marker.HLINE: '_'
    }

    colormap_map = {
        ColorMap.GRAY: 'Greys',
        ColorMap.PURPLE: 'Purples',
        ColorMap.BLUE: 'Blues',
        ColorMap.GREEN: 'Greens',
        ColorMap.ORANGE: 'Oranges',
        ColorMap.RED: 'Reds',
        ColorMap.YELLOW_BROWN: 'YlOrBr',
        ColorMap.YELLOW_RED: 'YlOrRd',
        ColorMap.ORANGE_RED: 'OrRd',
        ColorMap.PURPLE_RED: 'PuRd',
        ColorMap.RED_PURPLE: 'RdPu',
        ColorMap.BLUE_PURPLE: 'BuPu',
        ColorMap.GREEN_BLUE: 'GnBu',
        ColorMap.PURPLE_BLUE: 'PuBu',
        ColorMap.YELLOW_GREEN_BLUE: 'YlGnBu',
        ColorMap.PURPLE_BLUE_GREEN: 'PuBuGn',
        ColorMap.BLUE_GREEN: 'BuGn',
        ColorMap.YELLO_GREEN: 'YlGn'
    }

    def __init__(self):
        self._frame: Frame = None
        self._chart: Chart = None
        self._fig = None
        self._idx = 0

    def set_frame(self, frame):
        self._frame = frame
        plt.figure(figsize=(frame.width_px//100, frame.height_px//100))

    def add_chart(self, chart):
        if self._chart:
            self._apply_chart_props()
        self._idx += 1
        self._fig = plt.subplot(self._frame.nrows, self._frame.ncols, self._idx)
        self._chart = chart

    def show(self):
        self._apply_chart_props()
        plt.show()

    def _apply_chart_props(self):
        if self._chart.legend_location:
            self._fig.legend(loc=MatplotlibBackend.loc_map[self._chart.legend_location])

        if self._chart.title:
            fontdict = {}
            if self._chart.title_font:
                fontdict['color'] = self._chart.title_font.color.to_array()
                fontdict['size'] = self._chart.title_font.size
            self._fig.set_title(self._chart.title, fontdict=fontdict)

        if self._chart.x_axis.font:
            self._fig.tick_params(
                axis='x',
                color=self._chart.x_axis.font.color.to_array(),
                labelcolor=self._chart.x_axis.font.color.to_array(),
                labelsize=self._chart.x_axis.font.size
            )
        if self._chart.x_axis.limits:
            self._fig.set_xlim(*self._chart.x_axis.limits)
        if self._chart.x_axis.label:
            fontdict = {}
            if self._chart.x_axis.font:
                fontdict['color'] = self._chart.x_axis.font.color.to_array()
                fontdict['size'] = self._chart.x_axis.font.size
            self._fig.set_xlabel(self._chart.x_axis.label, fontdict=fontdict)
        if self._chart.x_axis.ticks:
            self._fig.set_xticks(self._chart.x_axis.ticks)
        if self._chart.x_axis.tick_labels:
            self._fig.axes.set_xticklabels(self._chart.x_axis.tick_labels)

        if self._chart.y_axis.font:
            self._fig.tick_params(
                axis='y',
                color=self._chart.y_axis.font.color.to_array(),
                labelcolor=self._chart.y_axis.font.color.to_array(),
                labelsize=self._chart.y_axis.font.size
            )
        if self._chart.y_axis.limits:
            self._fig.set_ylim(*self._chart.y_axis.limits)
        if self._chart.y_axis.label:
            fontdict = {}
            if self._chart.y_axis.font:
                fontdict['color'] = self._chart.y_axis.font.color.to_array()
                fontdict['size'] = self._chart.y_axis.font.size
            self._fig.set_ylabel(self._chart.y_axis.label, fontdict=fontdict)
        if self._chart.y_axis.ticks:
            self._fig.set_yticks(self._chart.y_axis.ticks)
        if self._chart.y_axis.tick_labels:
            self._fig.axes.set_yticklabels(self._chart.y_axis.tick_labels)

        self._fig.grid(self._chart.grid)

        if self._chart.origin:
            ax = self._fig.axes
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')
            ax.xaxis.set_ticks_position('bottom')
            ax.spines['bottom'].set_position(('data', self._chart.origin[1]))
            # ax.spines['bottom'].set_position('zero')
            ax.yaxis.set_ticks_position('left')
            ax.spines['left'].set_position(('data', self._chart.origin[0]))

        if self._chart.show_axes:
            self._fig.set_axis_on()
        else:
            self._fig.set_axis_off()

    def draw_hbar(self, legend: str, values: List[float], color: Color, height: float):
        if legend and not self._chart.legend_location:
            self._chart.legend_location = LegendLocation.BEST
        yvals = list(range(len(values)))
        self._fig.barh(yvals, values, label=legend, color=color.to_array(), height=height)

    def draw_line(self, legend: str, y: List[float], color: Color, linewidth: float, linestyle: LineStyle, marker: Marker):
        if legend and not self._chart.legend_location:
            self._chart.legend_location = LegendLocation.BEST
        xvals = list(range(len(y)))
        self._fig.plot(
            xvals, y,
            label=legend,
            color=color.to_array(),
            linewidth=linewidth,
            linestyle=MatplotlibBackend.style_map[linestyle],
            marker=MatplotlibBackend.marker_map[marker]
        )

    def draw_vbar(self, legend: str, values: List[float], color: Color, width: float):
        if legend and not self._chart.legend_location:
            self._chart.legend_location = LegendLocation.BEST
        xvals = list(range(len(values)))
        self._fig.bar(xvals, values, label=legend, color=color.to_array(), width=width)

    def draw_scatter(self, legend: str, x: List[float], y: List[float], color: Color, marker: Marker):
        if legend and not self._chart.legend_location:
            self._chart.legend_location = LegendLocation.BEST
        marker = MatplotlibBackend.marker_map[marker]
        self._fig.plot(x, y, marker, label=legend, color=color.to_array())

    def draw_graph(self, legend: str, x: List[float], y: List[float], color: Color, linewidth: float, linestyle: LineStyle):
        if legend and not self._chart.legend_location:
            self._chart.legend_location = LegendLocation.BEST
        linestyle = MatplotlibBackend.style_map[linestyle]
        self._fig.plot(x, y, label=legend, color=color.to_array(), linewidth=linewidth, linestyle=linestyle)

    def draw_grayimg(self, img, colormap):
        self._fig.imshow(img, cmap=self.colormap_map[colormap])

    def draw_rgbimg(self, img):
        self._fig.imshow(img)

    def draw_stem(self, legend: str, x: List[float], y: List[float], color: Color, linewidth: float, linestyle: LineStyle, marker: Marker):
        if legend and not self._chart.legend_location:
            self._chart.legend_location = LegendLocation.BEST
        markerline, stemlines, baseline = self._fig.stem(x, y)
        linestyle = MatplotlibBackend.style_map[linestyle]
        marker = MatplotlibBackend.marker_map[marker]
        for stemline in stemlines:
            plt.setp(stemline, color=color.to_array(), linewidth=linewidth, linestyle=linestyle)
        plt.setp(markerline, color=color.to_array(), marker=marker)
        plt.setp(baseline, color=[78/255, 78/255, 78/255])
