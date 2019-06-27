'''The classes with sliders need the Bokeh server, i.e. to run this example
at the command line enter: bokeh serve --show SpotPlotLPSliderExample.py
To use the SpotPlotSlider (i.e. without a line plot) just import and
instantiate that instead (same init parameters)
The example data is the 3D grid used in the ColourMapLPSlider example.
The SpotPlotLPSlider class is for 1D data sections defined at arbitrary
x and y coordinates on a common z grid, so we'll subsample the 3D grid at a
number of random x and y coordinates to illustrate. The first and last points
are set to the corners of the grid. Using this approach, the spot
colours can be directly compared with the ColourMapLPSlider example.'''

import numpy

from bokeh.io import curdoc

from bokcolmaps import SpotPlotLPSlider
from bokcolmaps.Examples import example_data

xg, yg, z, Dg = example_data()

ns = 20  # Number of grid samples
# Select random x and y coordinates
xi = numpy.floor(numpy.random.rand(ns)*xg.size).astype(int)
yi = numpy.floor(numpy.random.rand(ns)*yg.size).astype(int)
# Set first and last points to corners of grid (makes colour mapping same
# as for ColourMapLPSlider example)
xi[0], yi[0] = 0, 0
xi[-1], yi[-1] = xg.size-1, yg.size-1

x, y = xg[xi], yg[yi]
D = numpy.zeros((z.size, ns))
for n in range(ns):
    D[:, n] = Dg[:, yi[n], xi[n]]

sp = SpotPlotLPSlider(x, y, z, D, cfile='../jet.txt',
                      xlab='x val', ylab='y val', zlab='power val',
                      dmlab='Function val')

curdoc().add_root(sp)
