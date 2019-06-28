# -*- coding: utf-8 -*-
# pragma: no cover
import os
import sys

import cnxcommon.ident_hash
from zope.deprecation import deprecated


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


here = os.path.abspath(os.path.dirname(__file__))
migrations = os.path.join(here, 'migrations')


sys.modules['cnxdb.ident_hash'] = deprecated(
    cnxcommon.ident_hash,
    'cnxdb.ident_hash is now cnxcommon.ident_hash.',
)
