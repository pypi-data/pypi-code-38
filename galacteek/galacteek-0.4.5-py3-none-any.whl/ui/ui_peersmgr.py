# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/peersmgr.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PeersManager(object):
    def setupUi(self, PeersManager):
        PeersManager.setObjectName("PeersManager")
        PeersManager.resize(639, 422)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(PeersManager)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(PeersManager)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.peersCountLabel = QtWidgets.QLabel(PeersManager)
        self.peersCountLabel.setText("")
        self.peersCountLabel.setObjectName("peersCountLabel")
        self.horizontalLayout_3.addWidget(self.peersCountLabel)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_2 = QtWidgets.QLabel(PeersManager)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.search = QtWidgets.QLineEdit(PeersManager)
        self.search.setMaximumSize(QtCore.QSize(250, 16777215))
        self.search.setMaxLength(128)
        self.search.setObjectName("search")
        self.horizontalLayout_3.addWidget(self.search)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.tree = QtWidgets.QTreeView(PeersManager)
        self.tree.setObjectName("tree")
        self.verticalLayout.addWidget(self.tree)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(PeersManager)
        QtCore.QMetaObject.connectSlotsByName(PeersManager)

    def retranslateUi(self, PeersManager):
        _translate = QtCore.QCoreApplication.translate
        PeersManager.setWindowTitle(_translate("PeersManager", "Form"))
        self.label.setText(_translate("PeersManager", "Peers registered"))
        self.label_2.setText(_translate("PeersManager", "Search"))

