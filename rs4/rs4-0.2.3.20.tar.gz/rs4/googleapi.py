# backward compatible
from .apis.google import *

import warnings

warnings.simplefilter('default')
warnings.warn (
   "rs.googleapi will be deprecated, use rs3.apis.google",
    DeprecationWarning
)
