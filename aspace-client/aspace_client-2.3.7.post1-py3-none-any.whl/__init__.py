r"""
This package contains methods and classes that target ArchivesSpace's v2.X 
API.
"""

import aspace.enums
import aspace.util
import aspace.jsonmodel
import aspace.base_client
import aspace.client

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
