# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\uart_config_widget.ui',
# licensing of 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\uart_config_widget.ui' applies.
#
# Created: Fri Jun 28 13:34:09 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 201)
        self.formLayout = QtWidgets.QFormLayout(Form)
        self.formLayout.setObjectName("formLayout")
        self.portLabel = QtWidgets.QLabel(Form)
        self.portLabel.setObjectName("portLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.portLabel)
        self.portComboBox = QtWidgets.QComboBox(Form)
        self.portComboBox.setObjectName("portComboBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.portComboBox)
        self.baudRateComboBox = QtWidgets.QComboBox(Form)
        self.baudRateComboBox.setObjectName("baudRateComboBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.baudRateComboBox)
        self.parityComboBox = QtWidgets.QComboBox(Form)
        self.parityComboBox.setObjectName("parityComboBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.parityComboBox)
        self.stopBitsComboBox = QtWidgets.QComboBox(Form)
        self.stopBitsComboBox.setObjectName("stopBitsComboBox")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.stopBitsComboBox)
        self.baudRateLabel = QtWidgets.QLabel(Form)
        self.baudRateLabel.setObjectName("baudRateLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.baudRateLabel)
        self.parityLabel = QtWidgets.QLabel(Form)
        self.parityLabel.setObjectName("parityLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.parityLabel)
        self.stopBitsLabel = QtWidgets.QLabel(Form)
        self.stopBitsLabel.setObjectName("stopBitsLabel")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.stopBitsLabel)
        self.statusLabel = QtWidgets.QLabel(Form)
        self.statusLabel.setStyleSheet("QLabel {color: red; }")
        self.statusLabel.setText("")
        self.statusLabel.setObjectName("statusLabel")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.statusLabel)
        self.controlWidget = QtWidgets.QWidget(Form)
        self.controlWidget.setObjectName("controlWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.controlWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelButton = QtWidgets.QPushButton(self.controlWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.okButton = QtWidgets.QPushButton(self.controlWidget)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.controlWidget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.portLabel.setText(QtWidgets.QApplication.translate("Form", "Port", None, -1))
        self.baudRateLabel.setText(QtWidgets.QApplication.translate("Form", "Baud rate", None, -1))
        self.parityLabel.setText(QtWidgets.QApplication.translate("Form", "Parity", None, -1))
        self.stopBitsLabel.setText(QtWidgets.QApplication.translate("Form", "Stop bits", None, -1))
        self.cancelButton.setText(QtWidgets.QApplication.translate("Form", "Cancel", None, -1))
        self.okButton.setText(QtWidgets.QApplication.translate("Form", "OK", None, -1))

