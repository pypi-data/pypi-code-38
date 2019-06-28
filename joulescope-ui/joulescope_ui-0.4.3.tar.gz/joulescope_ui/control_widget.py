# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\control_widget.ui',
# licensing of 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\control_widget.ui' applies.
#
# Created: Fri Jun 28 13:34:09 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_ControlDockWidget(object):
    def setupUi(self, ControlDockWidget):
        ControlDockWidget.setObjectName("ControlDockWidget")
        ControlDockWidget.resize(754, 480)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.playButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.playButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/joulescope/resources/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.playButton.setIcon(icon)
        self.playButton.setCheckable(True)
        self.playButton.setFlat(True)
        self.playButton.setObjectName("playButton")
        self.horizontalLayout.addWidget(self.playButton)
        self.recordButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.recordButton.setEnabled(True)
        self.recordButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/joulescope/resources/record.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.recordButton.setIcon(icon1)
        self.recordButton.setCheckable(True)
        self.recordButton.setFlat(True)
        self.recordButton.setObjectName("recordButton")
        self.horizontalLayout.addWidget(self.recordButton)
        self.iRangeLabel = QtWidgets.QLabel(self.dockWidgetContents)
        self.iRangeLabel.setObjectName("iRangeLabel")
        self.horizontalLayout.addWidget(self.iRangeLabel)
        self.iRangeComboBox = QtWidgets.QComboBox(self.dockWidgetContents)
        self.iRangeComboBox.setObjectName("iRangeComboBox")
        self.horizontalLayout.addWidget(self.iRangeComboBox)
        self.vRangeLabel = QtWidgets.QLabel(self.dockWidgetContents)
        self.vRangeLabel.setObjectName("vRangeLabel")
        self.horizontalLayout.addWidget(self.vRangeLabel)
        self.vRangeComboBox = QtWidgets.QComboBox(self.dockWidgetContents)
        self.vRangeComboBox.setObjectName("vRangeComboBox")
        self.horizontalLayout.addWidget(self.vRangeComboBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.energyNameLabel = QtWidgets.QLabel(self.dockWidgetContents)
        self.energyNameLabel.setObjectName("energyNameLabel")
        self.horizontalLayout.addWidget(self.energyNameLabel)
        self.energyValueLabel = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.energyValueLabel.setFont(font)
        self.energyValueLabel.setObjectName("energyValueLabel")
        self.horizontalLayout.addWidget(self.energyValueLabel)
        ControlDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(ControlDockWidget)
        QtCore.QMetaObject.connectSlotsByName(ControlDockWidget)

    def retranslateUi(self, ControlDockWidget):
        ControlDockWidget.setWindowTitle(QtWidgets.QApplication.translate("ControlDockWidget", "Control", None, -1))
        self.playButton.setToolTip(QtWidgets.QApplication.translate("ControlDockWidget", "Enable to capture data from the selected Joulescope.  Disable to stop/pause capture.", None, -1))
        self.recordButton.setToolTip(QtWidgets.QApplication.translate("ControlDockWidget", "Click once to start recording capture Joulescope data to a file.  Click again to stop the capture.  Only new data is recorded.", None, -1))
        self.iRangeLabel.setText(QtWidgets.QApplication.translate("ControlDockWidget", "Current Range", None, -1))
        self.iRangeComboBox.setToolTip(QtWidgets.QApplication.translate("ControlDockWidget", "Select the Joulescope current range.  \"Auto\" allows Joulescope to dynamical adjust the current range.", None, -1))
        self.vRangeLabel.setText(QtWidgets.QApplication.translate("ControlDockWidget", "Voltage Range", None, -1))
        self.vRangeComboBox.setToolTip(QtWidgets.QApplication.translate("ControlDockWidget", "The voltage range.  No autoranging option exists.", None, -1))
        self.energyNameLabel.setText(QtWidgets.QApplication.translate("ControlDockWidget", "Energy", None, -1))
        self.energyValueLabel.setText(QtWidgets.QApplication.translate("ControlDockWidget", "0 J", None, -1))

from . import joulescope_rc
