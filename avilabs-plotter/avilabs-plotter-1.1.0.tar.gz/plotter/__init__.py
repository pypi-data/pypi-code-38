# flake8: noqa
from .backends.matplotlib_backend import MatplotlibBackend
from .numeric.graph import Graph
from .frame import Frame
from .color import Color, ColorMap
from .font import Font
from .enums import LegendLocation, LineStyle, Marker
from .singletons import set_backend
from .axis import Axis
from .category.line import Line
from .category.horizontal_bar import HorizontalBar
from .category.vertical_bar import VerticalBar
from .numeric.scatter import Scatter
from .images.grayscale_image import GrayscaleImage
from .images.rgb_image import RgbImage
from .numeric.stem import Stem


def show_plot(title, plot):
    frame = Frame()
    chart = frame.create_chart()
    chart.title = title
    chart.add(plot)
    frame.show()

def show_chart(title, plots):
    frame = Frame()
    chart = frame.create_chart()
    chart.title = title
    chart.legend_location = LegendLocation.UPPER_RIGHT
    for plot in plots:
        chart.add(plot)
    frame.show()

def show_frame(nrows, ncols, height_px, width_px, titles, plot_charts):
    if nrows * ncols != len(plot_charts):
        raise ValueError(f'{nrows} x {ncols} != {len(plot_charts)}')
    if len(titles) != len(plot_charts):
        raise ValueError('Number of titles do not match number of plot charts')

    frame = Frame(height_px=height_px, width_px=width_px)
    frame.layout(nrows=nrows, ncols=ncols)

    num_charts = len(plot_charts)
    for title, plots in zip(titles, plot_charts):
        chart = frame.create_chart()
        chart.title = title
        for plot in plots:
            chart.add(plot)

    frame.show()
