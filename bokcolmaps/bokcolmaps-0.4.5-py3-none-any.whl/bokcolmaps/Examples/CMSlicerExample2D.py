''' This class needs the Bokeh server,
i.e. to run this example at the command line enter:
bokeh serve --show CMSlicerExample2D.py
'''

import numpy
from bokeh.io import curdoc

from bokcolmaps import CMSlicer
from bokcolmaps.Examples import example_data

x, y, z, D = example_data()
z = numpy.array([z[0]])
D = D[0]

cm = CMSlicer(x, y, z, D, cfile='../jet.txt',
              xlab='x val', ylab='y val', zlab='power val',
              dmlab='Function val')

curdoc().add_root(cm)
