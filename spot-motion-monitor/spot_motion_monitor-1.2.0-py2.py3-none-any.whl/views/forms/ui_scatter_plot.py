# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/scatter_plot.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ScatterPlot(object):
    def setupUi(self, ScatterPlot):
        ScatterPlot.setObjectName("ScatterPlot")
        ScatterPlot.resize(558, 494)
        self.gridLayout = QtWidgets.QGridLayout(ScatterPlot)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = QtWidgets.QWidget(ScatterPlot)
        self.widget.setMinimumSize(QtCore.QSize(100, 100))
        self.widget.setObjectName("widget")
        self.gridLayout.addWidget(self.widget, 1, 0, 1, 1)
        self.scatterPlot = GraphicsLayoutWidget(ScatterPlot)
        self.scatterPlot.setMinimumSize(QtCore.QSize(300, 300))
        self.scatterPlot.setObjectName("scatterPlot")
        self.gridLayout.addWidget(self.scatterPlot, 0, 1, 1, 1)
        self.yHistogram = GraphicsLayoutWidget(ScatterPlot)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.yHistogram.sizePolicy().hasHeightForWidth())
        self.yHistogram.setSizePolicy(sizePolicy)
        self.yHistogram.setMinimumSize(QtCore.QSize(100, 300))
        self.yHistogram.setObjectName("yHistogram")
        self.gridLayout.addWidget(self.yHistogram, 0, 0, 1, 1)
        self.xHistogram = GraphicsLayoutWidget(ScatterPlot)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.xHistogram.sizePolicy().hasHeightForWidth())
        self.xHistogram.setSizePolicy(sizePolicy)
        self.xHistogram.setMinimumSize(QtCore.QSize(300, 100))
        self.xHistogram.setObjectName("xHistogram")
        self.gridLayout.addWidget(self.xHistogram, 1, 1, 1, 1)
        self.gridLayout.setColumnMinimumWidth(0, 100)
        self.gridLayout.setColumnMinimumWidth(1, 300)
        self.gridLayout.setRowMinimumHeight(0, 300)
        self.gridLayout.setRowMinimumHeight(1, 100)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setRowStretch(0, 1)

        self.retranslateUi(ScatterPlot)
        QtCore.QMetaObject.connectSlotsByName(ScatterPlot)

    def retranslateUi(self, ScatterPlot):
        _translate = QtCore.QCoreApplication.translate
        ScatterPlot.setWindowTitle(_translate("ScatterPlot", "Form"))

from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ScatterPlot = QtWidgets.QWidget()
    ui = Ui_ScatterPlot()
    ui.setupUi(ScatterPlot)
    ScatterPlot.show()
    sys.exit(app.exec_())

