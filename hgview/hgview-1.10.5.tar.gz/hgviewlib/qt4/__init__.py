# -*- coding: utf-8 -*-
# Copyright (c) 2003-2012 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

#
# make sure the Qt rc files are converted into python modules, then load them
# this must be done BEFORE other hgqv qt4 modules are loaded.
import os
import os.path as osp
import sys
import datetime as dt

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
sip.setapi('QDate', 2)
sip.setapi('QDateTime', 2)
sip.setapi('QTextStream', 2)
sip.setapi('QTime', 2)
sip.setapi('QUrl', 2)

def should_rebuild(srcfile, pyfile):
    if getattr(sys, "frozen", False): # Py2exe specific: module embedded in
        return False                  # the executable and have no file
    return not osp.isfile(pyfile) or osp.isfile(srcfile) and \
               osp.getmtime(pyfile) < osp.getmtime(srcfile)

# automatically load resource module, creating it on the fly if
# required
curdir = osp.dirname(__file__)
pyfile = osp.join(curdir, "hgqv_rc.py")
rcfile = osp.join(curdir, "hgqv.qrc")
if should_rebuild(rcfile, pyfile):
    if os.system('pyrcc4 %s -o %s' % (rcfile, pyfile)):
        print "ERROR: Cannot convert the resource file '%s' into a python module." % rcfile
        print "Please check the PyQt 'pyrcc4' tool is installed, or do it by hand running:"
        print "pyrcc4 %s -o %s" % (rcfile, pyfile)

# load icons from resource and store them in a dict, no matter their
# extension (.svg or .png)
from PyQt4 import QtCore
from PyQt4 import QtGui, uic
import hgqv_rc


_icons = {}
def _load_icons():
    t = dt.date.today()
    x = t.month == 12 and t.day in (24,25)
    d = QtCore.QDir(':/icons')
    for icn in d.entryList():
        name, ext = osp.splitext(str(icn))
        if name not in _icons or ext == ".svg":
            _icons[name] = QtGui.QIcon(':/icons/%s' % icn)
    if x:
        for name in _icons:
            if name.endswith('_x'):
                _icons[name[:-2]] = _icons[name]

def icon(name):
    """
    Return a QIcon for the resource named 'name.(svg|png)' (the given
    'name' parameter must *not* provide the extension).
    """
    if not _icons:
        _load_icons()
    return _icons.get(name)


# dirty hack to please PyQt4 uic
import hgfileview
sys.modules['hgfileview'] = hgfileview
sys.modules['hgqv_rc'] = hgqv_rc

def setup_font_substitutions():
    # be sure monospace default font for diffs have a decent substitution
    # on MacOS
    QtGui.QFont.insertSubstitutions('monospace', ['monaco', 'courier new'])
