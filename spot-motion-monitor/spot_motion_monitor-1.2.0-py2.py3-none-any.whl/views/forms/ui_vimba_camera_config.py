# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/vimba_camera_config.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VimbaCameraConfigForm(object):
    def setupUi(self, VimbaCameraConfigForm):
        VimbaCameraConfigForm.setObjectName("VimbaCameraConfigForm")
        VimbaCameraConfigForm.resize(322, 166)
        self.gridLayout = QtWidgets.QGridLayout(VimbaCameraConfigForm)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.roiSizeLabel = QtWidgets.QLabel(VimbaCameraConfigForm)
        self.roiSizeLabel.setObjectName("roiSizeLabel")
        self.horizontalLayout_3.addWidget(self.roiSizeLabel)
        self.roiSizeLineEdit = QtWidgets.QLineEdit(VimbaCameraConfigForm)
        self.roiSizeLineEdit.setObjectName("roiSizeLineEdit")
        self.horizontalLayout_3.addWidget(self.roiSizeLineEdit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.roiFluxMinLabel = QtWidgets.QLabel(VimbaCameraConfigForm)
        self.roiFluxMinLabel.setObjectName("roiFluxMinLabel")
        self.horizontalLayout_2.addWidget(self.roiFluxMinLabel)
        self.roiFluxMinLineEdit = QtWidgets.QLineEdit(VimbaCameraConfigForm)
        self.roiFluxMinLineEdit.setObjectName("roiFluxMinLineEdit")
        self.horizontalLayout_2.addWidget(self.roiFluxMinLineEdit)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.roiExposureTimeLabel = QtWidgets.QLabel(VimbaCameraConfigForm)
        self.roiExposureTimeLabel.setObjectName("roiExposureTimeLabel")
        self.horizontalLayout.addWidget(self.roiExposureTimeLabel)
        self.roiExposureTimeLineEdit = QtWidgets.QLineEdit(VimbaCameraConfigForm)
        self.roiExposureTimeLineEdit.setObjectName("roiExposureTimeLineEdit")
        self.horizontalLayout.addWidget(self.roiExposureTimeLineEdit)
        self.roiExposureTimeUnits = QtWidgets.QLabel(VimbaCameraConfigForm)
        self.roiExposureTimeUnits.setTextFormat(QtCore.Qt.RichText)
        self.roiExposureTimeUnits.setObjectName("roiExposureTimeUnits")
        self.horizontalLayout.addWidget(self.roiExposureTimeUnits)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 3, 0, 1, 1)
        self.roiSizeLabel.setBuddy(self.roiSizeLineEdit)
        self.roiFluxMinLabel.setBuddy(self.roiFluxMinLineEdit)
        self.roiExposureTimeLabel.setBuddy(self.roiExposureTimeLineEdit)

        self.retranslateUi(VimbaCameraConfigForm)
        QtCore.QMetaObject.connectSlotsByName(VimbaCameraConfigForm)

    def retranslateUi(self, VimbaCameraConfigForm):
        _translate = QtCore.QCoreApplication.translate
        VimbaCameraConfigForm.setWindowTitle(_translate("VimbaCameraConfigForm", "Form"))
        self.roiSizeLabel.setText(_translate("VimbaCameraConfigForm", "ROI Size:"))
        self.roiSizeLineEdit.setToolTip(_translate("VimbaCameraConfigForm", "Valid Range: 20 to 1000 as an integer"))
        self.roiFluxMinLabel.setText(_translate("VimbaCameraConfigForm", "ROI Flux Minimum:"))
        self.roiFluxMinLineEdit.setToolTip(_translate("VimbaCameraConfigForm", "Valid Range: 100 to 10000 as an integer"))
        self.roiExposureTimeLabel.setText(_translate("VimbaCameraConfigForm", "ROI Exposure Time:"))
        self.roiExposureTimeLineEdit.setToolTip(_translate("VimbaCameraConfigForm", "Valid Range: 500 to 50000 as an integer"))
        self.roiExposureTimeUnits.setText(_translate("VimbaCameraConfigForm", "<html><head/><body><p>&#956;sec</p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    VimbaCameraConfigForm = QtWidgets.QWidget()
    ui = Ui_VimbaCameraConfigForm()
    ui.setupUi(VimbaCameraConfigForm)
    VimbaCameraConfigForm.show()
    sys.exit(app.exec_())

