import os
from .logging.decorators import debug


@debug.args
@debug.result
def which(name):
    """Attempt to find a binary file like the system this is being run upon."""
    for path_dir in os.environ['PATH'].split(os.pathsep):
        abs_name = os.path.join(os.path.expandvars(path_dir), name)
        if os.path.isfile(abs_name):
            return abs_name
    return None
