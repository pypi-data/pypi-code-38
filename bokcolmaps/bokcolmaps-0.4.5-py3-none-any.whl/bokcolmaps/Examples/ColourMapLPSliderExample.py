''' The classes with sliders need the Bokeh server,
i.e. to run this example at the command line enter:
bokeh serve --show ColourMapLPSliderExample.py

To use the ColourMapSlider (i.e. without a line plot)
just import and instantiate that instead (same init parameters)
To disable the hover tool readout, add kwarg hoverdisp=False.
This seems to speed up the line plot updates (TBD - find out why)
'''

from bokeh.io import curdoc

from bokcolmaps import ColourMapLPSlider
from bokcolmaps.Examples import example_data

x, y, z, D = example_data()

cm = ColourMapLPSlider(x, y, z, D, cfile='../jet.txt',
                       xlab='x val', ylab='y val', zlab='power val',
                       dmlab='Function val', hoverdisp=False)

curdoc().add_root(cm)
