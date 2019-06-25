__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "dwapstra"

from .connection import FxosConnection, FxosServiceList

# import other connections so they can be found via plugin discovery
from .ftd.connection import FtdConnection


