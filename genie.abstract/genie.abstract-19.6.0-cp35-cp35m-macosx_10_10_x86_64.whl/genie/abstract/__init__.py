__version__ = '19.6.0'

import re
import sys

from .magic import Lookup
from .decorator import LookupDecorator as lookup
from .package import AbstractPackage
from .token import AbstractToken

# try to record usage statistics
#  - only internal cisco users will have stats.CesMonitor module
#  - below code does nothing for DevNet users -  we DO NOT track usage stats
#    for PyPI/public/customer users
try:
    # new internal cisco-only pkg since devnet release
    from ats.cisco.stats import CesMonitor
except Exception:
    try:
        # legacy pyats version, stats was inside utils module
        from ats.utils.stats import CesMonitor
    except Exception:
        CesMonitor = None

finally:
    if CesMonitor is not None:
        # CesMonitor exists -> this is an internal cisco user
        CesMonitor(action = __name__, application='Genie').post()
        CesMonitor(action = __name__, application='pyATS Packages').post()


_IMPORTMAP = {
    re.compile(r'^abstract(?=$|\.)'): 'genie.abstract'
}

__all__ = ['Lookup', 'LookupDecorator']

def declare_package(name):
    '''declare_package

    declare an abstraction package. This api should be called at the top of your
    abstraction package's __init__.py file.

    Argument
    --------
        name (str): module fully qualified name (eg, __name__)

    Example
    -------
        >>> from genie import abstract
        >>> abstract.declare_package(__name__)
    '''

    try:
        # get the module object
        module = sys.modules[name]

    except KeyError:

        # module not loaded/non-existent.
        raise ValueError("'%s' is not a valid module." % name)

    # instanciate the abstraction package
    # (always delay to avoid circular reference due to recursive import)
    module.__abstract_pkg = AbstractPackage(name, delay = True)



def declare_token(name):
    '''declare_token

    declare an abstraction token. This api should be called at the top of your
    abstraction token module's __init__.py file.

    Argument
    --------
        name (str): module fully qualified name (eg, __name__)

    Example
    -------
        >>> from genie import abstract
        >>> abstract.declare_token(__name__)
    '''

    try:
        # get the module object
        module = sys.modules[name]

    except KeyError:

        # module not loaded/non-existent.
        raise ValueError("'%s' is not a valid module." % name)

    # mark it as an abstraction token
    module.__abstract_token = AbstractToken(name)
