'''To run this example at the command line enter:
python3 ColourMapExample.py'''

import numpy

from bokeh.plotting import show

from bokcolmaps import ColourMap
from bokcolmaps.Examples import example_data

x, y, z, D = example_data()
D = D[0]  # Data for first value of z
z = numpy.array([z[0]])  # First value of z

cm = ColourMap(x, y, z, D, cfile='../jet.txt',
               xlab='x val', ylab='y val', zlab='power val',
               dmlab='Function val')

# Calls below not needed, only added for code coverage test
cm.update_cbar(0)

show(cm)
