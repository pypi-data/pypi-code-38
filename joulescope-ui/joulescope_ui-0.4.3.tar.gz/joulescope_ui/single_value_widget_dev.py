# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\single_value_widget_dev.ui',
# licensing of 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\single_value_widget_dev.ui' applies.
#
# Created: Fri Jun 28 13:34:09 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(387, 76)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setObjectName("widget")
        self.formLayout = QtWidgets.QFormLayout(self.widget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.fieldLabel = QtWidgets.QLabel(self.widget)
        self.fieldLabel.setObjectName("fieldLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.fieldLabel)
        self.fieldComboBox = QtWidgets.QComboBox(self.widget)
        self.fieldComboBox.setObjectName("fieldComboBox")
        self.fieldComboBox.addItem("")
        self.fieldComboBox.addItem("")
        self.fieldComboBox.addItem("")
        self.fieldComboBox.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.fieldComboBox)
        self.statisticLabel = QtWidgets.QLabel(self.widget)
        self.statisticLabel.setObjectName("statisticLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.statisticLabel)
        self.statisticComboBox = QtWidgets.QComboBox(self.widget)
        self.statisticComboBox.setObjectName("statisticComboBox")
        self.statisticComboBox.addItem("")
        self.statisticComboBox.addItem("")
        self.statisticComboBox.addItem("")
        self.statisticComboBox.addItem("")
        self.statisticComboBox.addItem("")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.statisticComboBox)
        self.horizontalLayout.addWidget(self.widget)
        spacerItem = QtWidgets.QSpacerItem(44, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.widget_2 = QtWidgets.QWidget(Form)
        self.widget_2.setStyleSheet("QWidget { background-color : black; }\n"
"QLabel { color : green; font-weight: bold; font-size: 32pt; }")
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.valueLabel = QtWidgets.QLabel(self.widget_2)
        self.valueLabel.setLineWidth(0)
        self.valueLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.valueLabel.setObjectName("valueLabel")
        self.horizontalLayout_2.addWidget(self.valueLabel)
        self.unitLabel = QtWidgets.QLabel(self.widget_2)
        self.unitLabel.setLineWidth(0)
        self.unitLabel.setObjectName("unitLabel")
        self.horizontalLayout_2.addWidget(self.unitLabel)
        self.horizontalLayout.addWidget(self.widget_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.fieldLabel.setText(QtWidgets.QApplication.translate("Form", "Field", None, -1))
        self.fieldComboBox.setItemText(0, QtWidgets.QApplication.translate("Form", "Current", None, -1))
        self.fieldComboBox.setItemText(1, QtWidgets.QApplication.translate("Form", "Voltage", None, -1))
        self.fieldComboBox.setItemText(2, QtWidgets.QApplication.translate("Form", "Power", None, -1))
        self.fieldComboBox.setItemText(3, QtWidgets.QApplication.translate("Form", "Energy", None, -1))
        self.statisticLabel.setText(QtWidgets.QApplication.translate("Form", "Statistic", None, -1))
        self.statisticComboBox.setItemText(0, QtWidgets.QApplication.translate("Form", "mean", None, -1))
        self.statisticComboBox.setItemText(1, QtWidgets.QApplication.translate("Form", "standard deviation", None, -1))
        self.statisticComboBox.setItemText(2, QtWidgets.QApplication.translate("Form", "minimum", None, -1))
        self.statisticComboBox.setItemText(3, QtWidgets.QApplication.translate("Form", "maximum", None, -1))
        self.statisticComboBox.setItemText(4, QtWidgets.QApplication.translate("Form", "peak-to-peak", None, -1))
        self.valueLabel.setText(QtWidgets.QApplication.translate("Form", "0.000", None, -1))
        self.unitLabel.setText(QtWidgets.QApplication.translate("Form", " mA ", None, -1))

from . import joulescope_rc
