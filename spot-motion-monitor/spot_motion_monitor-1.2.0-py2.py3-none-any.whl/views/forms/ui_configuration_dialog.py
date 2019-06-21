# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/configuration_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ConfigurationDialog(object):
    def setupUi(self, ConfigurationDialog):
        ConfigurationDialog.setObjectName("ConfigurationDialog")
        ConfigurationDialog.resize(324, 302)
        self.verticalLayout = QtWidgets.QVBoxLayout(ConfigurationDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(ConfigurationDialog)
        self.tabWidget.setMinimumSize(QtCore.QSize(300, 250))
        self.tabWidget.setObjectName("tabWidget")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(ConfigurationDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ConfigurationDialog)
        self.tabWidget.setCurrentIndex(-1)
        self.buttonBox.accepted.connect(ConfigurationDialog.accept)
        self.buttonBox.rejected.connect(ConfigurationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ConfigurationDialog)

    def retranslateUi(self, ConfigurationDialog):
        _translate = QtCore.QCoreApplication.translate
        ConfigurationDialog.setWindowTitle(_translate("ConfigurationDialog", "Dialog"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ConfigurationDialog = QtWidgets.QDialog()
    ui = Ui_ConfigurationDialog()
    ui.setupUi(ConfigurationDialog)
    ConfigurationDialog.show()
    sys.exit(app.exec_())

