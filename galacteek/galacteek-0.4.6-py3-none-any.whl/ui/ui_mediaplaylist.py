# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/mediaplaylist.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MediaPlaylist(object):
    def setupUi(self, MediaPlaylist):
        MediaPlaylist.setObjectName("MediaPlaylist")
        MediaPlaylist.resize(441, 328)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(MediaPlaylist)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.savePlaylistButton = QtWidgets.QToolButton(MediaPlaylist)
        self.savePlaylistButton.setObjectName("savePlaylistButton")
        self.horizontalLayout.addWidget(self.savePlaylistButton)
        self.loadPlaylistButton = QtWidgets.QToolButton(MediaPlaylist)
        self.loadPlaylistButton.setObjectName("loadPlaylistButton")
        self.horizontalLayout.addWidget(self.loadPlaylistButton)
        self.clearButton = QtWidgets.QToolButton(MediaPlaylist)
        self.clearButton.setObjectName("clearButton")
        self.horizontalLayout.addWidget(self.clearButton)
        self.clipPlaylistButton = QtWidgets.QToolButton(MediaPlaylist)
        self.clipPlaylistButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/share/icons/clipboard.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.clipPlaylistButton.setIcon(icon)
        self.clipPlaylistButton.setObjectName("clipPlaylistButton")
        self.horizontalLayout.addWidget(self.clipPlaylistButton)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.previousButton = QtWidgets.QPushButton(MediaPlaylist)
        self.previousButton.setText("")
        self.previousButton.setObjectName("previousButton")
        self.horizontalLayout_2.addWidget(self.previousButton)
        self.nextButton = QtWidgets.QPushButton(MediaPlaylist)
        self.nextButton.setText("")
        self.nextButton.setObjectName("nextButton")
        self.horizontalLayout_2.addWidget(self.nextButton)
        self.horizontalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.listView = QtWidgets.QListView(MediaPlaylist)
        self.listView.setObjectName("listView")
        self.verticalLayout_3.addWidget(self.listView)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(MediaPlaylist)
        QtCore.QMetaObject.connectSlotsByName(MediaPlaylist)

    def retranslateUi(self, MediaPlaylist):
        _translate = QtCore.QCoreApplication.translate
        MediaPlaylist.setWindowTitle(_translate("MediaPlaylist", "Form"))
        self.savePlaylistButton.setText(_translate("MediaPlaylist", "Save playlist"))
        self.loadPlaylistButton.setText(_translate("MediaPlaylist", "Load playlist"))
        self.clearButton.setText(_translate("MediaPlaylist", "Clear"))
        self.previousButton.setToolTip(_translate("MediaPlaylist", "<html><head/><body><p>Previous</p></body></html>"))
        self.nextButton.setToolTip(_translate("MediaPlaylist", "<html><head/><body><p>Next</p></body></html>"))

from . import galacteek_rc
