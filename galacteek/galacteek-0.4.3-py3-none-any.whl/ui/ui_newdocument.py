# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/newdocument.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NewDocumentForm(object):
    def setupUi(self, NewDocumentForm):
        NewDocumentForm.setObjectName("NewDocumentForm")
        NewDocumentForm.resize(597, 335)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(NewDocumentForm)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.textEdit = QtWidgets.QTextEdit(NewDocumentForm)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(NewDocumentForm)
        self.label.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.filename = QtWidgets.QLineEdit(NewDocumentForm)
        self.filename.setMaximumSize(QtCore.QSize(1024, 16777215))
        self.filename.setMaxLength(256)
        self.filename.setObjectName("filename")
        self.horizontalLayout.addWidget(self.filename)
        self.importButton = QtWidgets.QPushButton(NewDocumentForm)
        self.importButton.setObjectName("importButton")
        self.horizontalLayout.addWidget(self.importButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(NewDocumentForm)
        QtCore.QMetaObject.connectSlotsByName(NewDocumentForm)

    def retranslateUi(self, NewDocumentForm):
        _translate = QtCore.QCoreApplication.translate
        NewDocumentForm.setWindowTitle(_translate("NewDocumentForm", "Form"))
        self.label.setText(_translate("NewDocumentForm", "File name"))
        self.importButton.setToolTip(_translate("NewDocumentForm", "<html><head/><body><p>Import this document to IPFS</p></body></html>"))
        self.importButton.setText(_translate("NewDocumentForm", "Import"))

