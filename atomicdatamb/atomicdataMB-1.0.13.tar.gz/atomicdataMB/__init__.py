from .g_values import RadPresConst, gValue
from .photolossrates import PhotoRate
from .initialize_atomicdata import initialize_atomicdata
from .atomicmass import atomicmass


name = 'atomicdataMB'
__author__ = 'Matthew Burger'
__email__ = 'mburger@stsci.edu'
__version__ = '1.0.13'

# Verify the database is setup correctly
try:
    initialize_atomicdata()
except:
    print('database initialization failed')
