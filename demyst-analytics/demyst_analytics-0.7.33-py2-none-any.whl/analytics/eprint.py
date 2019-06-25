from __future__ import print_function
import sys
import os
# https://stackoverflow.com/a/14981125/8264
def debug(*args, **kwargs):
    if(os.environ.get('DEBUG', None)):
        print(*args, file=sys.stderr, **kwargs)
