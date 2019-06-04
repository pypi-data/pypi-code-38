# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/hashmarksmgr.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_HashmarksViewForm(object):
    def setupUi(self, HashmarksViewForm):
        HashmarksViewForm.setObjectName("HashmarksViewForm")
        HashmarksViewForm.resize(534, 390)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(HashmarksViewForm)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.toolbox = QtWidgets.QToolBox(HashmarksViewForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolbox.sizePolicy().hasHeightForWidth())
        self.toolbox.setSizePolicy(sizePolicy)
        self.toolbox.setObjectName("toolbox")
        self.page = QtWidgets.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 514, 341))
        self.page.setObjectName("page")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.expandButton = QtWidgets.QToolButton(self.page)
        self.expandButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/share/icons/expand.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.expandButton.setIcon(icon)
        self.expandButton.setCheckable(True)
        self.expandButton.setObjectName("expandButton")
        self.horizontalLayout.addWidget(self.expandButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.treeMarks = QtWidgets.QTreeView(self.page)
        self.treeMarks.setObjectName("treeMarks")
        self.treeMarks.header().setDefaultSectionSize(100)
        self.treeMarks.header().setStretchLastSection(True)
        self.verticalLayout_3.addWidget(self.treeMarks)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.toolbox.addItem(self.page, "")
        self.verticalLayout.addWidget(self.toolbox)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(HashmarksViewForm)
        self.toolbox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(HashmarksViewForm)

    def retranslateUi(self, HashmarksViewForm):
        _translate = QtCore.QCoreApplication.translate
        HashmarksViewForm.setWindowTitle(_translate("HashmarksViewForm", "Form"))
        self.expandButton.setToolTip(_translate("HashmarksViewForm", "<html><head/><body><p>Expand</p></body></html>"))
        self.toolbox.setItemText(self.toolbox.indexOf(self.page), _translate("HashmarksViewForm", "Local hashmarks"))

from . import galacteek_rc
