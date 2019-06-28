# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\error_window.ui',
# licensing of 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\error_window.ui' applies.
#
# Created: Fri Jun 28 13:34:09 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_ErrorWindow(object):
    def setupUi(self, ErrorWindow):
        ErrorWindow.setObjectName("ErrorWindow")
        ErrorWindow.resize(600, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/joulescope/resources/icon_64x64.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ErrorWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(ErrorWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        ErrorWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(ErrorWindow)
        QtCore.QMetaObject.connectSlotsByName(ErrorWindow)

    def retranslateUi(self, ErrorWindow):
        ErrorWindow.setWindowTitle(QtWidgets.QApplication.translate("ErrorWindow", "Joulescope UI Error", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("ErrorWindow", "TextLabel", None, -1))

from . import joulescope_rc
