# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\uart_widget.ui',
# licensing of 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\uart_widget.ui' applies.
#
# Created: Fri Jun 28 13:34:09 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(652, 515)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setEnabled(False)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.textEntryWidget = QtWidgets.QWidget(Form)
        self.textEntryWidget.setObjectName("textEntryWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.textEntryWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.textEntryWidget)
        self.lineEdit.setEnabled(False)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.configButton = QtWidgets.QPushButton(self.textEntryWidget)
        self.configButton.setObjectName("configButton")
        self.horizontalLayout.addWidget(self.configButton)
        self.verticalLayout.addWidget(self.textEntryWidget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.configButton.setText(QtWidgets.QApplication.translate("Form", "Configure", None, -1))

