# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\meter_widget_dev.ui',
# licensing of 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\meter_widget_dev.ui' applies.
#
# Created: Fri Jun 28 13:34:09 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(478, 681)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setStyleSheet("QLabel { background-color : black; color : green; font-weight: bold; font-size: 48pt; }")
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setStyleSheet("QLabel { background-color : black; color : green; font-weight: bold; font-size: 48pt; }")
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setStyleSheet("QLabel { background-color : black; color : green; font-weight: bold; font-size: 48pt; }")
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setStyleSheet("QLabel { background-color : black; color : green; font-weight: bold; font-size: 48pt; }")
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.updateRateLabel = QtWidgets.QLabel(self.frame)
        self.updateRateLabel.setObjectName("updateRateLabel")
        self.horizontalLayout.addWidget(self.updateRateLabel)
        self.updateRateSpinBox = QtWidgets.QSpinBox(self.frame)
        self.updateRateSpinBox.setObjectName("updateRateSpinBox")
        self.horizontalLayout.addWidget(self.updateRateSpinBox)
        self.hzLabel = QtWidgets.QLabel(self.frame)
        self.hzLabel.setObjectName("hzLabel")
        self.horizontalLayout.addWidget(self.hzLabel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Form", " TextLabel", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Form", "TextLabel", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("Form", "TextLabel", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("Form", "TextLabel", None, -1))
        self.updateRateLabel.setText(QtWidgets.QApplication.translate("Form", "Update Rate", None, -1))
        self.hzLabel.setText(QtWidgets.QApplication.translate("Form", "Hz", None, -1))
        self.pushButton.setText(QtWidgets.QApplication.translate("Form", "Switch to Oscillosope", None, -1))

from . import joulescope_rc
