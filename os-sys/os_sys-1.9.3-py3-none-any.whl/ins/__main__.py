from __future__ import absolute_import

import os
import sys

# If we are running from a wheel, add the wheel to sys.path
# This allows the usage python ins-*.whl/ins install ins-*.whl
if __package__ == '':
    # __file__ is ins-*.whl/ins/__main__.py
    # first dirname call strips of '/__main__.py', second strips off '/ins'
    # Resulting path is the name of the wheel itself
    # Add that to sys.path so we can import ins
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)

from ins._internal import main as _main  # isort:skip # noqa

if __name__ == '__main__':
    sys.exit(_main())
