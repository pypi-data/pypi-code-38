'''To run this example at the command line enter: python3 SpotPlotExample.py
The example data is the 3D grid used in the ColourMap example. The SpotPlot
class is for 1D data sections defined at arbitrary x and y coordinates on a
common z grid, so we'll  subsample the 3D grid at a number of random x and y
coordinates to illustrate. The first and last points are set to the corners of
the grid. Using this approach, the spot colours can be directly compared with
the ColourMap example.'''

import numpy

from bokeh.plotting import show

from bokcolmaps import SpotPlot
from bokcolmaps.Examples import example_data

xg, yg, z, Dg = example_data()

ns = 20  # Number of grid samples
# Select random x and y coordinates
xi = numpy.floor(numpy.random.rand(ns)*xg.size).astype(int)
yi = numpy.floor(numpy.random.rand(ns)*yg.size).astype(int)
# Set first and last points to corners of grid (makes colour mapping same as
# for ColourMapLPSlider example)
xi[0], yi[0] = 0, 0
xi[-1], yi[-1] = xg.size-1, yg.size-1

x, y = xg[xi], yg[yi]
D = numpy.zeros(ns)
for n in range(ns):
    D[n] = Dg[0, yi[n], xi[n]]  # Data for first value of z
z = z[0]  # First value of z

sp = SpotPlot(x, y, z, D, cfile='../jet.txt',
              xlab='x val', ylab='y val', zlab='power val',
              dmlab='Function val')

# Calls below not needed, only added for code coverage test
sp.convert_data()
sp.changed(0)
sp.update_cbar()

show(sp)
