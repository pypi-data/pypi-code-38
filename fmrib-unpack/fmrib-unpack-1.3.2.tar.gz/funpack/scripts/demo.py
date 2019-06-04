#!/usr/bin/env python
#
# demo.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import sys
import os.path as op

import notebook.notebookapp as notebookapp
import bash_kernel.install  as bash_kernel_install


def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]

    thisdir = op.abspath(op.dirname(__file__))
    nbdir = op.join(thisdir, 'demo')
    bash_kernel_install.main([])
    notebookapp.main(['--notebook-dir', nbdir] + argv)


if __name__ == '__main__':
    main()
