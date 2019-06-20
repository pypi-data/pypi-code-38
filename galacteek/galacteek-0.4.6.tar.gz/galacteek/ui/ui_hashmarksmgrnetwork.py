# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/hashmarksmgrnetwork.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NetworkHashmarksViewForm(object):
    def setupUi(self, NetworkHashmarksViewForm):
        NetworkHashmarksViewForm.setObjectName("NetworkHashmarksViewForm")
        NetworkHashmarksViewForm.resize(541, 374)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(NetworkHashmarksViewForm)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.expandButton = QtWidgets.QToolButton(NetworkHashmarksViewForm)
        self.expandButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/share/icons/expand.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.expandButton.setIcon(icon)
        self.expandButton.setCheckable(True)
        self.expandButton.setObjectName("expandButton")
        self.horizontalLayout.addWidget(self.expandButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.search = QtWidgets.QLineEdit(NetworkHashmarksViewForm)
        self.search.setObjectName("search")
        self.horizontalLayout.addWidget(self.search)
        self.searchButton = QtWidgets.QPushButton(NetworkHashmarksViewForm)
        self.searchButton.setObjectName("searchButton")
        self.horizontalLayout.addWidget(self.searchButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.treeNetMarks = QtWidgets.QTreeView(NetworkHashmarksViewForm)
        self.treeNetMarks.setObjectName("treeNetMarks")
        self.verticalLayout.addWidget(self.treeNetMarks)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(NetworkHashmarksViewForm)
        QtCore.QMetaObject.connectSlotsByName(NetworkHashmarksViewForm)

    def retranslateUi(self, NetworkHashmarksViewForm):
        _translate = QtCore.QCoreApplication.translate
        NetworkHashmarksViewForm.setWindowTitle(_translate("NetworkHashmarksViewForm", "Form"))
        self.searchButton.setText(_translate("NetworkHashmarksViewForm", "Search"))

from . import galacteek_rc
