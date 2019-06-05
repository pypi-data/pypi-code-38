# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/profilepostmessage.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PostMessageDialog(object):
    def setupUi(self, PostMessageDialog):
        PostMessageDialog.setObjectName("PostMessageDialog")
        PostMessageDialog.resize(511, 319)
        self.verticalLayout = QtWidgets.QVBoxLayout(PostMessageDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.message = QtWidgets.QTextEdit(PostMessageDialog)
        self.message.setObjectName("message")
        self.gridLayout.addWidget(self.message, 3, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(PostMessageDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(PostMessageDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.title = QtWidgets.QLineEdit(PostMessageDialog)
        self.title.setMaxLength(256)
        self.title.setObjectName("title")
        self.gridLayout.addWidget(self.title, 1, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(PostMessageDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(PostMessageDialog)
        self.buttonBox.accepted.connect(PostMessageDialog.accept)
        self.buttonBox.rejected.connect(PostMessageDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PostMessageDialog)

    def retranslateUi(self, PostMessageDialog):
        _translate = QtCore.QCoreApplication.translate
        PostMessageDialog.setWindowTitle(_translate("PostMessageDialog", "Post a message"))
        self.label_2.setText(_translate("PostMessageDialog", "Title"))
        self.label.setText(_translate("PostMessageDialog", "Message"))

