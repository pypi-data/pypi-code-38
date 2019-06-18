"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from PyQt5 import QtCore, QtGui, QtWidgets


class DragDropMainWindow(QtWidgets.QMainWindow):
    # dropped must be defined out here for things to work.
    dropped = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent):
        if a0.mimeData().hasUrls:
            a0.accept()
        else:
            a0.ignore()

    def dragMoveEvent(self, a0: QtGui.QDragMoveEvent):
        if a0.mimeData().hasUrls:
            a0.setDropAction(QtCore.Qt.CopyAction)
            a0.accept()
        else:
            a0.ignore()

    def dropEvent(self, a0: QtGui.QDropEvent):
        if a0.mimeData().hasUrls:
            a0.setDropAction(QtCore.Qt.CopyAction)
            a0.accept()
            links = []
            for url in a0.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.dropped.emit(links)
        else:
            a0.ignore()
