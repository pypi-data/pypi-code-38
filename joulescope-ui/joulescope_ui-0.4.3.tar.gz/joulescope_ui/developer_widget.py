# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\developer_widget.ui',
# licensing of 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\developer_widget.ui' applies.
#
# Created: Fri Jun 28 13:34:09 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_DeveloperDockWidget(object):
    def setupUi(self, DeveloperDockWidget):
        DeveloperDockWidget.setObjectName("DeveloperDockWidget")
        DeveloperDockWidget.resize(662, 1135)
        DeveloperDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.parameter_groupbox = QtWidgets.QGroupBox(self.dockWidgetContents)
        self.parameter_groupbox.setObjectName("parameter_groupbox")
        self.parameter_layout = QtWidgets.QGridLayout(self.parameter_groupbox)
        self.parameter_layout.setObjectName("parameter_layout")
        self.verticalLayout.addWidget(self.parameter_groupbox)
        self.status_groupbox = QtWidgets.QGroupBox(self.dockWidgetContents)
        self.status_groupbox.setObjectName("status_groupbox")
        self.status_layout = QtWidgets.QGridLayout(self.status_groupbox)
        self.status_layout.setObjectName("status_layout")
        self.verticalLayout.addWidget(self.status_groupbox)
        spacerItem = QtWidgets.QSpacerItem(20, 461, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        DeveloperDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DeveloperDockWidget)
        QtCore.QMetaObject.connectSlotsByName(DeveloperDockWidget)

    def retranslateUi(self, DeveloperDockWidget):
        DeveloperDockWidget.setWindowTitle(QtWidgets.QApplication.translate("DeveloperDockWidget", "Developer", None, -1))
        self.parameter_groupbox.setTitle(QtWidgets.QApplication.translate("DeveloperDockWidget", "Device Parameters", None, -1))
        self.status_groupbox.setTitle(QtWidgets.QApplication.translate("DeveloperDockWidget", "Device Status", None, -1))

