# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/keys.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_KeysForm(object):
    def setupUi(self, KeysForm):
        KeysForm.setObjectName("KeysForm")
        KeysForm.resize(606, 407)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(KeysForm)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.addKeyButton = QtWidgets.QPushButton(KeysForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addKeyButton.sizePolicy().hasHeightForWidth())
        self.addKeyButton.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/share/icons/key-diago.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addKeyButton.setIcon(icon)
        self.addKeyButton.setIconSize(QtCore.QSize(16, 16))
        self.addKeyButton.setObjectName("addKeyButton")
        self.horizontalLayout.addWidget(self.addKeyButton, 0, QtCore.Qt.AlignLeft)
        self.deleteKeyButton = QtWidgets.QPushButton(KeysForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deleteKeyButton.sizePolicy().hasHeightForWidth())
        self.deleteKeyButton.setSizePolicy(sizePolicy)
        self.deleteKeyButton.setObjectName("deleteKeyButton")
        self.horizontalLayout.addWidget(self.deleteKeyButton, 0, QtCore.Qt.AlignLeft)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.retranslateUi(KeysForm)
        QtCore.QMetaObject.connectSlotsByName(KeysForm)

    def retranslateUi(self, KeysForm):
        _translate = QtCore.QCoreApplication.translate
        KeysForm.setWindowTitle(_translate("KeysForm", "Form"))
        self.addKeyButton.setText(_translate("KeysForm", "Add key"))
        self.deleteKeyButton.setText(_translate("KeysForm", "Delete"))

from . import galacteek_rc
