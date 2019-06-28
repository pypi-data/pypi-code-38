# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\preferences_dialog.ui',
# licensing of 'd:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\preferences_dialog.ui' applies.
#
# Created: Fri Jun 28 13:34:09 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName("PreferencesDialog")
        PreferencesDialog.resize(741, 780)
        PreferencesDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(PreferencesDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupListView = QtWidgets.QListView(self.widget)
        self.groupListView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.groupListView.setProperty("showDropIndicator", False)
        self.groupListView.setObjectName("groupListView")
        self.horizontalLayout.addWidget(self.groupListView)
        self.targetWidget = QtWidgets.QWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.targetWidget.sizePolicy().hasHeightForWidth())
        self.targetWidget.setSizePolicy(sizePolicy)
        self.targetWidget.setObjectName("targetWidget")
        self.formLayout = QtWidgets.QFormLayout(self.targetWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.horizontalLayout.addWidget(self.targetWidget)
        self.verticalLayout.addWidget(self.widget)
        self.buttonFrame = QtWidgets.QFrame(PreferencesDialog)
        self.buttonFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.buttonFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.buttonFrame.setObjectName("buttonFrame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.buttonFrame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.resetButton = QtWidgets.QPushButton(self.buttonFrame)
        self.resetButton.setObjectName("resetButton")
        self.horizontalLayout_2.addWidget(self.resetButton)
        self.cancelButton = QtWidgets.QPushButton(self.buttonFrame)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_2.addWidget(self.cancelButton)
        self.okButton = QtWidgets.QPushButton(self.buttonFrame)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout_2.addWidget(self.okButton)
        self.verticalLayout.addWidget(self.buttonFrame)

        self.retranslateUi(PreferencesDialog)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(QtWidgets.QApplication.translate("PreferencesDialog", "Preferences", None, -1))
        self.resetButton.setText(QtWidgets.QApplication.translate("PreferencesDialog", "Reset", None, -1))
        self.cancelButton.setText(QtWidgets.QApplication.translate("PreferencesDialog", "Cancel", None, -1))
        self.okButton.setText(QtWidgets.QApplication.translate("PreferencesDialog", "OK", None, -1))

