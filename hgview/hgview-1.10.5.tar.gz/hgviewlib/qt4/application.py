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

"""
Application utilities.
"""

import sys

from hgrepoviewer import FileViewer, FileDiffViewer, HgRepoViewer, ManifestViewer
from hgviewlib.application import HgViewApplication
from PyQt4 import QtGui, QtCore



class HgViewQtApplication(HgViewApplication):
    """
    HgView application using Qt.
    """
    FileViewer = FileViewer
    FileDiffViewer = FileDiffViewer
    HgRepoViewer = HgRepoViewer
    ManifestViewer = ManifestViewer

    def __init__(self, *args, **kwargs):
        # Initiate the application settings.
        # This allows to use the default QSettings constructor.
        QtCore.QCoreApplication.setOrganizationName("logilab")
        QtCore.QCoreApplication.setOrganizationDomain("logilab.org")
        QtCore.QCoreApplication.setApplicationName("hgview")
        # This import is critical for qt initialization (at least on Mac os X)
        import hgviewlib.qt4.hgqv_rc
        # make Ctrl+C works
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        app = QtGui.QApplication(sys.argv)
        from hgviewlib.qt4 import setup_font_substitutions
        setup_font_substitutions()

        super(HgViewQtApplication, self).__init__(*args, **kwargs)

        self.app = app

    def exec_(self):
        self.viewer.show()  #pylint: disable=E1103
        if '--profile' in sys.argv or '--time' in sys.argv:
            return 0
        return self.app.exec_()



