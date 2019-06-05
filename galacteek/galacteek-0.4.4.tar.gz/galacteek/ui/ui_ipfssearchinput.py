# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/ipfssearchinput.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SearchInput(object):
    def setupUi(self, SearchInput):
        SearchInput.setObjectName("SearchInput")
        SearchInput.resize(554, 43)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SearchInput.sizePolicy().hasHeightForWidth())
        SearchInput.setSizePolicy(sizePolicy)
        SearchInput.setMaximumSize(QtCore.QSize(16777215, 43))
        SearchInput.setStyleSheet("QWidget#SearchInput {\n"
"    border: 2px solid black;\n"
"}")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(SearchInput)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(SearchInput)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.searchQuery = QtWidgets.QLineEdit(SearchInput)
        self.searchQuery.setObjectName("searchQuery")
        self.horizontalLayout.addWidget(self.searchQuery)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(SearchInput)
        QtCore.QMetaObject.connectSlotsByName(SearchInput)

    def retranslateUi(self, SearchInput):
        _translate = QtCore.QCoreApplication.translate
        SearchInput.setWindowTitle(_translate("SearchInput", "Form"))
        self.label.setText(_translate("SearchInput", "Search the distributed web"))

