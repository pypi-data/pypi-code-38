from __future__ import print_function
import datetime
import os
import tempfile
import unittest

import numpy
import netCDF4

n = netCDF4.Dataset('delme.nc', 'w', format='NETCDF4')

n.Conventions = 'CF-1.7'

x = n.createDimension('x', 400)
y = n.createDimension('y' , 600)
    
humidity = n.createVariable('humidity', 'f8', ('y', 'x'), fill_value=-999.9,
                            chunksizes=(300, 400))
humidity.standard_name = "specific_humidity"
humidity[...] = numpy.arange(400*600)

n.close()

