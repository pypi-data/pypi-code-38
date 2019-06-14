# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/addkeydialog.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AddKeyDialog(object):
    def setupUi(self, AddKeyDialog):
        AddKeyDialog.setObjectName("AddKeyDialog")
        AddKeyDialog.resize(502, 145)
        self.gridLayout_2 = QtWidgets.QGridLayout(AddKeyDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.addKeyLayout = QtWidgets.QFormLayout()
        self.addKeyLayout.setObjectName("addKeyLayout")
        self.label = QtWidgets.QLabel(AddKeyDialog)
        self.label.setObjectName("label")
        self.addKeyLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(AddKeyDialog)
        self.label_2.setObjectName("label_2")
        self.addKeyLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.keyName = QtWidgets.QLineEdit(AddKeyDialog)
        self.keyName.setMaxLength(64)
        self.keyName.setObjectName("keyName")
        self.addKeyLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.keyName)
        self.keySize = QtWidgets.QComboBox(AddKeyDialog)
        self.keySize.setObjectName("keySize")
        self.keySize.addItem("")
        self.keySize.addItem("")
        self.addKeyLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.keySize)
        self.gridLayout_2.addLayout(self.addKeyLayout, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddKeyDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(AddKeyDialog)
        self.buttonBox.accepted.connect(AddKeyDialog.accept)
        self.buttonBox.rejected.connect(AddKeyDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddKeyDialog)

    def retranslateUi(self, AddKeyDialog):
        _translate = QtCore.QCoreApplication.translate
        AddKeyDialog.setWindowTitle(_translate("AddKeyDialog", "Dialog"))
        self.label.setText(_translate("AddKeyDialog", "Key name"))
        self.label_2.setText(_translate("AddKeyDialog", "Key size"))
        self.keySize.setItemText(0, _translate("AddKeyDialog", "2048"))
        self.keySize.setItemText(1, _translate("AddKeyDialog", "4096"))

