# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/addfeeddialog.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AddFeedDialog(object):
    def setupUi(self, AddFeedDialog):
        AddFeedDialog.setObjectName("AddFeedDialog")
        AddFeedDialog.resize(438, 181)
        self.verticalLayout = QtWidgets.QVBoxLayout(AddFeedDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.resourceLabel = QtWidgets.QLabel(AddFeedDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.resourceLabel.setFont(font)
        self.resourceLabel.setText("")
        self.resourceLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.resourceLabel.setObjectName("resourceLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.resourceLabel)
        self.label = QtWidgets.QLabel(AddFeedDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label)
        self.feedName = QtWidgets.QLineEdit(AddFeedDialog)
        self.feedName.setObjectName("feedName")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.feedName)
        self.label_2 = QtWidgets.QLabel(AddFeedDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.resolve = QtWidgets.QSpinBox(AddFeedDialog)
        self.resolve.setMinimum(20)
        self.resolve.setMaximum(2592000)
        self.resolve.setProperty("value", 3600)
        self.resolve.setObjectName("resolve")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.resolve)
        self.share = QtWidgets.QCheckBox(AddFeedDialog)
        self.share.setObjectName("share")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.share)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddFeedDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.buttonBox)
        self.autoPin = QtWidgets.QCheckBox(AddFeedDialog)
        self.autoPin.setChecked(False)
        self.autoPin.setObjectName("autoPin")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.autoPin)
        self.verticalLayout.addLayout(self.formLayout)

        self.retranslateUi(AddFeedDialog)
        self.buttonBox.accepted.connect(AddFeedDialog.accept)
        self.buttonBox.rejected.connect(AddFeedDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddFeedDialog)

    def retranslateUi(self, AddFeedDialog):
        _translate = QtCore.QCoreApplication.translate
        AddFeedDialog.setWindowTitle(_translate("AddFeedDialog", "Dialog"))
        self.label.setText(_translate("AddFeedDialog", "Feed name"))
        self.label_2.setText(_translate("AddFeedDialog", "Resolve frequency (seconds)"))
        self.share.setText(_translate("AddFeedDialog", "Share"))
        self.autoPin.setText(_translate("AddFeedDialog", "Auto PIN"))

