# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2012 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import os
import sys

user = object()     # Used to write/read user data.

USERROOT = os.path.expanduser('~')
USERHOME = os.path.join(USERROOT, '.trosnoth')


def getPath(module, *bits):
    if module is user:
        return getUserPath(*bits)

    if isinstance(module, bytes):
        module = module.decode('ascii')
    if isinstance(module, str):
        bits = (module,) + bits
        module = sys.modules['trosnoth.data']

    if _datapath is None:
        return os.path.join(os.path.dirname(module.__file__), *bits)
    return os.path.join(_datapath, module.__name__.replace('.', '/'), *bits)


def getUserPath(*bits):
    makeDirs(USERHOME)
    return os.path.join(USERHOME, *bits)


def getPandaPath(module, *bits):
    '''
    Performs the same function as getPath, but returns a path that is usable in
    calls to Panda functions.
    '''
    from panda3d.core import Filename

    path = getPath(module, *bits)
    pandaPath = Filename.fromOsSpecific(path)
    pandaPath.makeTrueCase()
    return pandaPath.getFullpath()


def makeDirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Check whether this is within a py2exe zip
def get_exe_dir():
    import imp, sys
    if (getattr(sys, "frozen", False) or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")): # tools/freeze
        return os.path.dirname(sys.executable)
    return None


_datapath = get_exe_dir()
