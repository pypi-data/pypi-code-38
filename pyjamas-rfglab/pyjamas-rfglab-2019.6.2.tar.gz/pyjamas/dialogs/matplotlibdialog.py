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

from typing import Tuple
import sys

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt as Qt
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout


class MatplotlibDialog(QDialog):
    _ZOOM_ACTION_INDEX_ = 5  # Index of the Zoom action in the NavigationToolbar (self.toolbar.actions()).

    def __init__(self, parent=None, figure: Figure = None, title: str = ''):
        super(MatplotlibDialog, self).__init__(parent)

        # a figure instance to plot on
        self.figure: Figure = figure

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas: FigureCanvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar: NavigationToolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        #self.button = QPushButton('Plot')
        #self.button.clicked.connect(self.plot)

        # set the layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        #layout.addWidget(self.button)
        self.setLayout(self.layout)

        # Add title.
        self.setWindowTitle(title)
        self.window_size: Tuple[int, int] = (self.width(), self.height())

        # Remove close/maximize/minimize buttons, and leave title bar. @todo: Remove?
        # https://doc.qt.io/archives/qtjambi-4.5.2_01/com/trolltech/qt/core/Qt.WindowType.html
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)

    def set_figure(self, figure: Figure = None) -> bool:
        if self.figure is not None:
            plt.close(self.figure)

        self.figure = figure
        self.canvas.figure = self.figure
        self.canvas.setParent(None)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar.canvas = self.canvas
        self.layout.addWidget(self.canvas)

        return True


    def get_figure(self) -> Figure:
        return self.figure


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = MatplotlibDialog()
    main.show()

    sys.exit(app.exec_())