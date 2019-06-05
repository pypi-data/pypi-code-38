from __future__ import absolute_import, print_function
import sys

from mercurial import (
    pycompat,
    util,
)

def main(argv):
    enc = util.urlreq.quote(pycompat.sysbytes(argv[1]))
    if pycompat.iswindows:
        fmt = 'file:///%s'
    else:
        fmt = 'file://%s'
    print(fmt % pycompat.sysstr(enc))

if __name__ == '__main__':
    main(sys.argv)
