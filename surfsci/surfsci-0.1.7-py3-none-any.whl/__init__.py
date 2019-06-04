__author__       = "David Kalliecharan"
__author_email__ = "david@david.science"
__license__      = "ISC"

try:
    from . import xps
    from . import scatter
except ImportError as err:
    print(err)
