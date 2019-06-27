'''generate_colourbar function definition'''

from bokeh.models import ColorBar
from bokeh.models.tickers import AdaptiveTicker


def generate_colourbar(cmap, cbarwidth=25):

    '''Generate a colourbar for the the ColourMap and SpotPlot classes'''

    cbar = ColorBar(color_mapper=cmap, location=(0, 0),
                    label_standoff=5, orientation='horizontal',
                    height=cbarwidth, ticker=AdaptiveTicker(),
                    border_line_color=None, bar_line_color='black',
                    major_tick_line_color='black',
                    minor_tick_line_color=None)

    return cbar
