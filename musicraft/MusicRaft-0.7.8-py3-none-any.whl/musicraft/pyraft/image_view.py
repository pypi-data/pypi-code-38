#!/usr/bin/env python
# -*- encoding: utf8 -*-
"""
Copyright 2015 Hippos Technical Systems BV.
(but borrows somme code from the painting/svgviewer example of PyQt v4.x)

@author: larry
"""

from PySide import QtCore, QtGui
import fitz
from PIL import Image, ImageQt

class ImageView(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)

        self.setWindowTitle("Image Viewer")
        self.resize(640, 480)


    def open(self, fileName):
        doc = fitz.open(fileName)
        page = doc[0]
        pix = page.getPixmap()
        #get data and display
        #pilimg = getMyPILImageDatFromCamera()
        #image = PILQT.ImageQt.ImageQt(pilimg)
        if 0:  # image.isNull():
            QtGui.QMessageBox.information(self, "Image Viewer","Cannot load %s." % fileName)
            return
        #self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
        img = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
        qtimg = ImageQt.ImageQt(img)
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(qtimg))
        self.imageLabel.adjustSize()


if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    imageView = ImageView()
    imageView.open(*sys.argv[1:])
    imageView.show()
    sys.exit(app.exec_())