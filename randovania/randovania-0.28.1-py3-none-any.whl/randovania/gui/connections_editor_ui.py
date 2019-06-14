# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/travis/build/randovania/randovania/randovania/gui/connections_editor.ui',
# licensing of '/home/travis/build/randovania/randovania/randovania/gui/connections_editor.ui' applies.
#
# Created: Fri Jun 14 21:12:30 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_ConnectionEditor(object):
    def setupUi(self, ConnectionEditor):
        ConnectionEditor.setObjectName("ConnectionEditor")
        ConnectionEditor.resize(600, 300)
        ConnectionEditor.setMinimumSize(QtCore.QSize(600, 0))
        self.gridLayout_2 = QtWidgets.QGridLayout(ConnectionEditor)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.visualizer_scroll = QtWidgets.QScrollArea(ConnectionEditor)
        self.visualizer_scroll.setWidgetResizable(True)
        self.visualizer_scroll.setObjectName("visualizer_scroll")
        self.visualizer_contents = QtWidgets.QWidget()
        self.visualizer_contents.setGeometry(QtCore.QRect(0, 0, 499, 251))
        self.visualizer_contents.setObjectName("visualizer_contents")
        self.gridLayout = QtWidgets.QGridLayout(self.visualizer_contents)
        self.gridLayout.setObjectName("gridLayout")
        self.visualizer_scroll.setWidget(self.visualizer_contents)
        self.gridLayout_2.addWidget(self.visualizer_scroll, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(ConnectionEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 0, 1, 1, 1)
        self.new_alternative_button = QtWidgets.QPushButton(ConnectionEditor)
        self.new_alternative_button.setObjectName("new_alternative_button")
        self.gridLayout_2.addWidget(self.new_alternative_button, 1, 0, 1, 1)

        self.retranslateUi(ConnectionEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ConnectionEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ConnectionEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(ConnectionEditor)

    def retranslateUi(self, ConnectionEditor):
        ConnectionEditor.setWindowTitle(QtWidgets.QApplication.translate("ConnectionEditor", "Connection Editor", None, -1))
        self.new_alternative_button.setText(QtWidgets.QApplication.translate("ConnectionEditor", "New Alternative", None, -1))

