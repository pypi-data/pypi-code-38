import sys

from .builder import (
    Builder,
    main
)

if sys.version_info.major < 3:
    warnings.simplefilter('always', DeprecationWarning)
    warnings.warn(DeprecationWarning(
        "This package does not support Python 2. Upgrade to Python 3."
    ))
    warnings.resetwarnings()
