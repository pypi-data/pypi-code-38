"""This package implements real-time data collection capabilities on top of the python environment.

In order to use Rookout data collection service, the following components are needed:
- The Rook module package (this package).
- The Rookout Agent.
- The Rookout Web Service.

For further information, checkout rookout.com.

This package can be used in two ways:
- Importing using "from rook import auto_start" will start the Rook using the default configuration.
- Importing "from rook import Rook" allows to manually configure and start the Rook.
"""

from .interface import start, flush, stop
