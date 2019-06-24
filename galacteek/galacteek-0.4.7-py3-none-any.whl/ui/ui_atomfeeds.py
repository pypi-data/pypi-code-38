# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/atomfeeds.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AtomFeeds(object):
    def setupUi(self, AtomFeeds):
        AtomFeeds.setObjectName("AtomFeeds")
        AtomFeeds.resize(503, 393)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(AtomFeeds)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.hLayout = QtWidgets.QHBoxLayout()
        self.hLayout.setContentsMargins(10, -1, 10, -1)
        self.hLayout.setSpacing(6)
        self.hLayout.setObjectName("hLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.addFeedButton = QtWidgets.QPushButton(AtomFeeds)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/share/icons/atom-feed.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addFeedButton.setIcon(icon)
        self.addFeedButton.setObjectName("addFeedButton")
        self.horizontalLayout.addWidget(self.addFeedButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.treeFeeds = QtWidgets.QTreeView(AtomFeeds)
        self.treeFeeds.setObjectName("treeFeeds")
        self.verticalLayout_2.addWidget(self.treeFeeds)
        self.hLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.addLayout(self.hLayout)

        self.retranslateUi(AtomFeeds)
        QtCore.QMetaObject.connectSlotsByName(AtomFeeds)

    def retranslateUi(self, AtomFeeds):
        _translate = QtCore.QCoreApplication.translate
        AtomFeeds.setWindowTitle(_translate("AtomFeeds", "Form"))
        self.addFeedButton.setText(_translate("AtomFeeds", "Subscribe to an Atom feed"))

from . import galacteek_rc
