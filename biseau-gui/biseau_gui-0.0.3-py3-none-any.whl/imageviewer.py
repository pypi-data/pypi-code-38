"""Implementation of a generalist image viewer"""
import os
import tempfile
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtSvg import *

from graphviz import Source


class ImageView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene())

        self.setBackgroundBrush(QBrush(Qt.white))
        # It appears that Qt can handle gif:
        #  https://stackoverflow.com/questions/41709464/python-pyqt-add-background-gif
        # so is biseau.gif_from_filenames and derivatives

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # creation of a temporary file to play with
        # with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.svg') as fd:
            # self.__tempname = fd.name

    # def __del__(self):
        # if self.__tempname:
            # os.unlink(self.__tempname)



    def wheelEvent(self, event):
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = self.mapToScene(event.pos())

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.mapToScene(event.pos())

        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())


    def set_dot(self, source):
        s = Source(source, format="svg")
        s.render('tmp')
        self.dot_item = QGraphicsSvgItem('tmp.svg')
        # print(self.__tempname[:-4])
        # print(self.__tempname)
        # s.render(self.__tempname[:-4])
        # self.dot_item = QGraphicsSvgItem(self.__tempname)
        # self.dot_item.renderer().setViewBox(QRect(0,0,1000,1000))

        # Fixed svg bug... Don't understand why this is required.
        # The renderer.viewBox is small and doesn't fit the itemBoundingRect which is the repaint area.
        self.dot_item.renderer().setViewBox(self.dot_item.boundingRect())

        self.scene().clear()
        self.scene().addItem(self.dot_item)

        # rect.setWidth(rect.width())
        # rect.setHeight(rect.height())

        # Center the view on dot_item
        self.scene().setSceneRect(self.dot_item.sceneBoundingRect())


class ImageViewer(QWidget):

    # exemple signals
    dotReceived = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image viewer")
        self.tool_bar = QToolBar()
        self.view = ImageView()

        _layout = QVBoxLayout()
        _layout.addWidget(self.tool_bar)
        _layout.addWidget(self.view)
        _layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(_layout)
        # self._setup_toolbar()  # TODO: do something with that toolbar


    def _setup_toolbar(self):
        "Populate the toolbar"
        # example connection simple
        self.tool_bar.addAction("act_1", lambda: print("act_1"))
        self.tool_bar.addAction("act_2", self.act_2)

        # example connection avec arguments
        self.combo = QComboBox()
        self.combo.addItems(["test1", "test2", "test3"])
        self.tool_bar.addWidget(self.combo)
        self.combo.currentTextChanged.connect(self.act_3)


    def set_dot(self, source: str):

        # with open("/media/sacha/Linux_data/dev/biseau-gui/d.dot") as file:
        #     data = file.read()
        self.view.set_dot(source)
