#!/usr/bin/env python
#
# __init__.py - funpack package
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


__version__ = '1.3.2'
"""The ``funpack`` versioning scheme roughly follows Semantic Versioning
conventions.
"""


from .custom    import (loader,    # noqa
                        sniffer,
                        formatter,
                        exporter,
                        processor,
                        metaproc,
                        cleaner)
from .datatable import (DataTable, # noqa
                        Column)
