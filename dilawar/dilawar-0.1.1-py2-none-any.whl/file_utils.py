"""file_utils.py: 

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import subprocess


def tail(f, n, offset=0):
    """Read n lines from the back of file.
    Work on UNIX systems only.
    """
    lines = subprocess.check_output( "tail -n %d %s" % (n+offset, f ), shell =
            True )
    return lines.decode( 'utf-8' )
