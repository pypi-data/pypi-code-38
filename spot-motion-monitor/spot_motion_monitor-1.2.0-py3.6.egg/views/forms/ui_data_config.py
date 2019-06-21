# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/data_config.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DataConfigForm(object):
    def setupUi(self, DataConfigForm):
        DataConfigForm.setObjectName("DataConfigForm")
        DataConfigForm.resize(326, 110)
        self.verticalLayout = QtWidgets.QVBoxLayout(DataConfigForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pixelScaleLabel = QtWidgets.QLabel(DataConfigForm)
        self.pixelScaleLabel.setObjectName("pixelScaleLabel")
        self.horizontalLayout.addWidget(self.pixelScaleLabel)
        self.pixelScaleLineEdit = QtWidgets.QLineEdit(DataConfigForm)
        self.pixelScaleLineEdit.setObjectName("pixelScaleLineEdit")
        self.horizontalLayout.addWidget(self.pixelScaleLineEdit)
        self.pixelScaleUnitsLabel = QtWidgets.QLabel(DataConfigForm)
        self.pixelScaleUnitsLabel.setObjectName("pixelScaleUnitsLabel")
        self.horizontalLayout.addWidget(self.pixelScaleUnitsLabel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 50, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.pixelScaleLabel.setBuddy(self.pixelScaleLineEdit)

        self.retranslateUi(DataConfigForm)
        QtCore.QMetaObject.connectSlotsByName(DataConfigForm)

    def retranslateUi(self, DataConfigForm):
        _translate = QtCore.QCoreApplication.translate
        DataConfigForm.setWindowTitle(_translate("DataConfigForm", "Form"))
        self.pixelScaleLabel.setText(_translate("DataConfigForm", "Pixel Scale:"))
        self.pixelScaleLineEdit.setToolTip(_translate("DataConfigForm", "Valid Range: 0 to 1e200 with a precision of 5"))
        self.pixelScaleUnitsLabel.setText(_translate("DataConfigForm", "arcsec/pixel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DataConfigForm = QtWidgets.QWidget()
    ui = Ui_DataConfigForm()
    ui.setupUi(DataConfigForm)
    DataConfigForm.show()
    sys.exit(app.exec_())

