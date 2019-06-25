#===============================================================================
# tempfifo.py
#===============================================================================

# Imports ======================================================================

import os
import tempfile




# Classes ======================================================================

class NamedTemporaryFIFO():
    """Create and return a temporary named pipe. The name of the pipe is
    accessible as the returned object's 'name' attribute. Can be used as a
    context manager. For example:
    
        with NamedTemporaryFIFO() as ntf:
            print(ntf.name)
    
    Upon exiting the context, the named pipe is removed unless the 'delete'
    parameter is set to False..

    Parameters
    ----------
    suffix : str or bytes
        as for tempfile.mkstemp
    prefix : sty or bytes
        as for tempfile.mkstemp
    dir : str or bytesq
        as for tempfile.mkstemp
    delete : bool
        whether the named pipe is deleted on exiting context (default True)

    Attributes
    ----------
    name : str
        filename of the temporary named pipe
    delete : bool
        whether the named pipe is deleted on exiting context (default True)
    """

    def __init__(self, suffix=None, prefix=None, dir=None, delete: bool = True):
        with tempfile.NamedTemporaryFile(
            suffix=suffix, prefix=prefix, dir=dir
        ) as t:
            self.name = t.name
        self.delete = delete
        os.mkfifo(self.name)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.delete:
            os.remove(self.name)
        return False
