# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/psd_plots_config.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PsdPlotConfigForm(object):
    def setupUi(self, PsdPlotConfigForm):
        PsdPlotConfigForm.setObjectName("PsdPlotConfigForm")
        PsdPlotConfigForm.resize(271, 293)
        self.verticalLayout = QtWidgets.QVBoxLayout(PsdPlotConfigForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.autoscaleX1dCheckBox = QtWidgets.QCheckBox(PsdPlotConfigForm)
        self.autoscaleX1dCheckBox.setEnabled(True)
        self.autoscaleX1dCheckBox.setChecked(True)
        self.autoscaleX1dCheckBox.setObjectName("autoscaleX1dCheckBox")
        self.verticalLayout.addWidget(self.autoscaleX1dCheckBox)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.x1dMaximumLabel = QtWidgets.QLabel(PsdPlotConfigForm)
        self.x1dMaximumLabel.setEnabled(False)
        self.x1dMaximumLabel.setObjectName("x1dMaximumLabel")
        self.horizontalLayout.addWidget(self.x1dMaximumLabel)
        self.x1dMaximumLineEdit = QtWidgets.QLineEdit(PsdPlotConfigForm)
        self.x1dMaximumLineEdit.setEnabled(False)
        self.x1dMaximumLineEdit.setObjectName("x1dMaximumLineEdit")
        self.horizontalLayout.addWidget(self.x1dMaximumLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.autoscaleY1dCheckBox = QtWidgets.QCheckBox(PsdPlotConfigForm)
        self.autoscaleY1dCheckBox.setEnabled(True)
        self.autoscaleY1dCheckBox.setChecked(True)
        self.autoscaleY1dCheckBox.setObjectName("autoscaleY1dCheckBox")
        self.verticalLayout.addWidget(self.autoscaleY1dCheckBox)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.y1dMaximumLabel = QtWidgets.QLabel(PsdPlotConfigForm)
        self.y1dMaximumLabel.setEnabled(False)
        self.y1dMaximumLabel.setObjectName("y1dMaximumLabel")
        self.horizontalLayout_2.addWidget(self.y1dMaximumLabel)
        self.y1dMaximumLineEdit = QtWidgets.QLineEdit(PsdPlotConfigForm)
        self.y1dMaximumLineEdit.setEnabled(False)
        self.y1dMaximumLineEdit.setObjectName("y1dMaximumLineEdit")
        self.horizontalLayout_2.addWidget(self.y1dMaximumLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.waterfallNumBinsLabel = QtWidgets.QLabel(PsdPlotConfigForm)
        self.waterfallNumBinsLabel.setEnabled(True)
        self.waterfallNumBinsLabel.setObjectName("waterfallNumBinsLabel")
        self.horizontalLayout_3.addWidget(self.waterfallNumBinsLabel)
        self.waterfallNumBinsLineEdit = QtWidgets.QLineEdit(PsdPlotConfigForm)
        self.waterfallNumBinsLineEdit.setObjectName("waterfallNumBinsLineEdit")
        self.horizontalLayout_3.addWidget(self.waterfallNumBinsLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.waterfallColorMapLabel = QtWidgets.QLabel(PsdPlotConfigForm)
        self.waterfallColorMapLabel.setEnabled(True)
        self.waterfallColorMapLabel.setObjectName("waterfallColorMapLabel")
        self.horizontalLayout_4.addWidget(self.waterfallColorMapLabel)
        self.waterfallColorMapComboBox = QtWidgets.QComboBox(PsdPlotConfigForm)
        self.waterfallColorMapComboBox.setEnabled(True)
        self.waterfallColorMapComboBox.setObjectName("waterfallColorMapComboBox")
        self.horizontalLayout_4.addWidget(self.waterfallColorMapComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        spacerItem = QtWidgets.QSpacerItem(20, 85, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.x1dMaximumLabel.setBuddy(self.x1dMaximumLineEdit)
        self.y1dMaximumLabel.setBuddy(self.y1dMaximumLineEdit)
        self.waterfallNumBinsLabel.setBuddy(self.waterfallNumBinsLineEdit)
        self.waterfallColorMapLabel.setBuddy(self.waterfallColorMapComboBox)

        self.retranslateUi(PsdPlotConfigForm)
        QtCore.QMetaObject.connectSlotsByName(PsdPlotConfigForm)

    def retranslateUi(self, PsdPlotConfigForm):
        _translate = QtCore.QCoreApplication.translate
        PsdPlotConfigForm.setWindowTitle(_translate("PsdPlotConfigForm", "Form"))
        self.autoscaleX1dCheckBox.setText(_translate("PsdPlotConfigForm", "Auto Scale X 1D"))
        self.x1dMaximumLabel.setText(_translate("PsdPlotConfigForm", "X 1D Maximum:"))
        self.autoscaleY1dCheckBox.setText(_translate("PsdPlotConfigForm", "Auto Scale Y 1D"))
        self.y1dMaximumLabel.setText(_translate("PsdPlotConfigForm", "Y 1D Maximum:"))
        self.waterfallNumBinsLabel.setText(_translate("PsdPlotConfigForm", "Waterfall Number of Bins:"))
        self.waterfallNumBinsLineEdit.setToolTip(_translate("PsdPlotConfigForm", "Valid Range: 1 to 1000 as an integer"))
        self.waterfallColorMapLabel.setText(_translate("PsdPlotConfigForm", "Waterfall Color Map:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PsdPlotConfigForm = QtWidgets.QWidget()
    ui = Ui_PsdPlotConfigForm()
    ui.setupUi(PsdPlotConfigForm)
    PsdPlotConfigForm.show()
    sys.exit(app.exec_())

