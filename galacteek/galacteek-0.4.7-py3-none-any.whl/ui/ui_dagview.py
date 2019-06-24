# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/dagview.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DagViewForm(object):
    def setupUi(self, DagViewForm):
        DagViewForm.setObjectName("DagViewForm")
        DagViewForm.resize(400, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DagViewForm)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.dagHash = QtWidgets.QLabel(DagViewForm)
        self.dagHash.setText("")
        self.dagHash.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.dagHash.setObjectName("dagHash")
        self.verticalLayout.addWidget(self.dagHash)
        self.dagTree = QtWidgets.QTreeWidget(DagViewForm)
        self.dagTree.setColumnCount(2)
        self.dagTree.setObjectName("dagTree")
        self.dagTree.headerItem().setText(0, "1")
        self.dagTree.headerItem().setText(1, "2")
        self.verticalLayout.addWidget(self.dagTree)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(DagViewForm)
        QtCore.QMetaObject.connectSlotsByName(DagViewForm)

    def retranslateUi(self, DagViewForm):
        _translate = QtCore.QCoreApplication.translate
        DagViewForm.setWindowTitle(_translate("DagViewForm", "Form"))

