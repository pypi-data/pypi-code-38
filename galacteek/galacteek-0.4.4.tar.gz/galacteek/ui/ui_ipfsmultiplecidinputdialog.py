# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/ipfsmultiplecidinputdialog.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MultipleCIDInputDialog(object):
    def setupUi(self, MultipleCIDInputDialog):
        MultipleCIDInputDialog.setObjectName("MultipleCIDInputDialog")
        MultipleCIDInputDialog.resize(745, 200)
        self.verticalLayout = QtWidgets.QVBoxLayout(MultipleCIDInputDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(MultipleCIDInputDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.cid = QtWidgets.QLineEdit(MultipleCIDInputDialog)
        self.cid.setObjectName("cid")
        self.horizontalLayout.addWidget(self.cid)
        self.addCidButton = QtWidgets.QPushButton(MultipleCIDInputDialog)
        self.addCidButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.addCidButton.setObjectName("addCidButton")
        self.horizontalLayout.addWidget(self.addCidButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.validity = QtWidgets.QLabel(MultipleCIDInputDialog)
        self.validity.setText("")
        self.validity.setAlignment(QtCore.Qt.AlignCenter)
        self.validity.setObjectName("validity")
        self.horizontalLayout_3.addWidget(self.validity)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cidList = QtWidgets.QListWidget(MultipleCIDInputDialog)
        self.cidList.setObjectName("cidList")
        self.horizontalLayout_2.addWidget(self.cidList)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(MultipleCIDInputDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(MultipleCIDInputDialog)
        self.buttonBox.accepted.connect(MultipleCIDInputDialog.accept)
        self.buttonBox.rejected.connect(MultipleCIDInputDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(MultipleCIDInputDialog)

    def retranslateUi(self, MultipleCIDInputDialog):
        _translate = QtCore.QCoreApplication.translate
        MultipleCIDInputDialog.setWindowTitle(_translate("MultipleCIDInputDialog", "Dialog"))
        self.label.setText(_translate("MultipleCIDInputDialog", "IPFS CID"))
        self.addCidButton.setToolTip(_translate("MultipleCIDInputDialog", "<html><head/><body><p>Add CID to the list</p></body></html>"))
        self.addCidButton.setText(_translate("MultipleCIDInputDialog", "+"))

