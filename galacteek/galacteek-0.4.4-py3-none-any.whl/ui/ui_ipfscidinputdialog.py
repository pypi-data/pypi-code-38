# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/ipfscidinputdialog.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CIDInputDialog(object):
    def setupUi(self, CIDInputDialog):
        CIDInputDialog.setObjectName("CIDInputDialog")
        CIDInputDialog.resize(676, 103)
        self.verticalLayout = QtWidgets.QVBoxLayout(CIDInputDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(CIDInputDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.cid = QtWidgets.QLineEdit(CIDInputDialog)
        self.cid.setMaxLength(256)
        self.cid.setObjectName("cid")
        self.horizontalLayout.addWidget(self.cid)
        self.clearButton = QtWidgets.QPushButton(CIDInputDialog)
        self.clearButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/share/icons/clear-all.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.clearButton.setIcon(icon)
        self.clearButton.setObjectName("clearButton")
        self.horizontalLayout.addWidget(self.clearButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.validity = QtWidgets.QLabel(CIDInputDialog)
        self.validity.setText("")
        self.validity.setAlignment(QtCore.Qt.AlignCenter)
        self.validity.setObjectName("validity")
        self.verticalLayout_2.addWidget(self.validity)
        self.buttonBox = QtWidgets.QDialogButtonBox(CIDInputDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.retranslateUi(CIDInputDialog)
        self.buttonBox.accepted.connect(CIDInputDialog.accept)
        self.buttonBox.rejected.connect(CIDInputDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CIDInputDialog)

    def retranslateUi(self, CIDInputDialog):
        _translate = QtCore.QCoreApplication.translate
        CIDInputDialog.setWindowTitle(_translate("CIDInputDialog", "Dialog"))
        self.label.setText(_translate("CIDInputDialog", "IPFS CID"))
        self.clearButton.setToolTip(_translate("CIDInputDialog", "<html><head/><body><p>Clear</p></body></html>"))
        self.clearButton.setShortcut(_translate("CIDInputDialog", "Ctrl+X"))

from . import galacteek_rc
