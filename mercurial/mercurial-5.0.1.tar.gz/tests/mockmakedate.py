# mock out util.makedate() to supply testable values

from __future__ import absolute_import

import os

from mercurial import pycompat
from mercurial.utils import dateutil

def mockmakedate():
    filename = os.path.join(os.environ['TESTTMP'], 'testtime')
    try:
        with open(filename, 'rb') as timef:
            time = float(timef.read()) + 1
    except IOError:
        time = 0.0
    with open(filename, 'wb') as timef:
        timef.write(pycompat.bytestr(time))
    return (time, 0)

dateutil.makedate = mockmakedate
