# FMQL Utilities (fmqlutils) 

import os
import re

"""
Base Directory for fmqlutils (Caching, Schema Typing, Reports) is VISTA_DATA_BASE_DIR.
By default it is '/data/vista/' but what happens if that location isn't set?

Specialize default base vista data location from shell or put into profile
    export FMQL_VISTA_DATA_BASE_DIR="/data/vistalocn/"

It is used with 
    from fmqlutils import VISTA_DATA_BASE_DIR
outside the module or
    from .. import VISTA_DATA_BASE_DIR 
from within
"""
VISTA_DATA_BASE_DIR = "/data/vista/" if os.environ.get("FMQL_VISTA_DATA_BASE_DIR") is None else re.sub(r'([^\/])$', '\\1/', os.environ.get("FMQL_VISTA_DATA_BASE_DIR"))
if not os.path.isdir(VISTA_DATA_BASE_DIR):
    raise Exception("fmqlutils module and submodules can't work - VISTA_DATA_BASE_DIR \"{}\" doesn't exist. Either _ln -s_ a real location to this directory OR set the environment variable \"FMQL_VISTA_DATA_BASE_DIR\" to the desired location".format(VISTA_DATA_BASE_DIR))

