# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/hashmarksmgrfeeds.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FeedsViewForm(object):
    def setupUi(self, FeedsViewForm):
        FeedsViewForm.setObjectName("FeedsViewForm")
        FeedsViewForm.resize(400, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(FeedsViewForm)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeFeeds = QtWidgets.QTreeView(FeedsViewForm)
        self.treeFeeds.setObjectName("treeFeeds")
        self.verticalLayout.addWidget(self.treeFeeds)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(FeedsViewForm)
        QtCore.QMetaObject.connectSlotsByName(FeedsViewForm)

    def retranslateUi(self, FeedsViewForm):
        _translate = QtCore.QCoreApplication.translate
        FeedsViewForm.setWindowTitle(_translate("FeedsViewForm", "Form"))

