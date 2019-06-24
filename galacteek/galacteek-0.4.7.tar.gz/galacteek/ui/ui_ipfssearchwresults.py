# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/ipfssearchwresults.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IPFSSearchResults(object):
    def setupUi(self, IPFSSearchResults):
        IPFSSearchResults.setObjectName("IPFSSearchResults")
        IPFSSearchResults.resize(493, 394)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(IPFSSearchResults)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.browser = QtWidgets.QTextBrowser(IPFSSearchResults)
        self.browser.setObjectName("browser")
        self.verticalLayout.addWidget(self.browser)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(IPFSSearchResults)
        QtCore.QMetaObject.connectSlotsByName(IPFSSearchResults)

    def retranslateUi(self, IPFSSearchResults):
        _translate = QtCore.QCoreApplication.translate
        IPFSSearchResults.setWindowTitle(_translate("IPFSSearchResults", "Form"))

