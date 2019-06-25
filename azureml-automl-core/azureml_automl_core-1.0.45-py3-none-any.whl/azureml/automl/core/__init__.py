# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Init for standard AutoML modules."""
import os
import sys

vendor_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "_vendor"))
sys.path.append(vendor_folder)

__all__ = []

try:
    from ._version import ver as VERSION
    __version__ = VERSION
except ImportError:
    VERSION = '0.0.0+dev'
    __version__ = VERSION
