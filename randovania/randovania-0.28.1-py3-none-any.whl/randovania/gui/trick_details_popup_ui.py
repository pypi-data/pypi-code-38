# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/travis/build/randovania/randovania/randovania/gui/trick_details_popup.ui',
# licensing of '/home/travis/build/randovania/randovania/randovania/gui/trick_details_popup.ui' applies.
#
# Created: Fri Jun 14 21:12:30 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_TrickDetailsPopup(object):
    def setupUi(self, TrickDetailsPopup):
        TrickDetailsPopup.setObjectName("TrickDetailsPopup")
        TrickDetailsPopup.resize(326, 228)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TrickDetailsPopup.sizePolicy().hasHeightForWidth())
        TrickDetailsPopup.setSizePolicy(sizePolicy)
        TrickDetailsPopup.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout = QtWidgets.QVBoxLayout(TrickDetailsPopup)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title_label = QtWidgets.QLabel(TrickDetailsPopup)
        self.title_label.setWordWrap(True)
        self.title_label.setObjectName("title_label")
        self.verticalLayout.addWidget(self.title_label)
        self.scroll_area = QtWidgets.QScrollArea(TrickDetailsPopup)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area_contents = QtWidgets.QWidget()
        self.scroll_area_contents.setGeometry(QtCore.QRect(0, 0, 312, 158))
        self.scroll_area_contents.setObjectName("scroll_area_contents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scroll_area_contents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.area_list_label = QtWidgets.QLabel(self.scroll_area_contents)
        self.area_list_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.area_list_label.setWordWrap(True)
        self.area_list_label.setObjectName("area_list_label")
        self.verticalLayout_2.addWidget(self.area_list_label)
        self.scroll_area.setWidget(self.scroll_area_contents)
        self.verticalLayout.addWidget(self.scroll_area)
        self.button_box = QtWidgets.QDialogButtonBox(TrickDetailsPopup)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.button_box.setObjectName("button_box")
        self.verticalLayout.addWidget(self.button_box)

        self.retranslateUi(TrickDetailsPopup)
        QtCore.QMetaObject.connectSlotsByName(TrickDetailsPopup)

    def retranslateUi(self, TrickDetailsPopup):
        TrickDetailsPopup.setWindowTitle(QtWidgets.QApplication.translate("TrickDetailsPopup", "Item Configuration", None, -1))
        self.title_label.setText(QtWidgets.QApplication.translate("TrickDetailsPopup", "<html><head/><body><p>{trick} with level {level} can be used in the rooms listed next.</p><p>Click a room name to open it in the Data Visualizer for more details.</p></body></html>", None, -1))
        self.area_list_label.setText(QtWidgets.QApplication.translate("TrickDetailsPopup", "<html><head/><body><p><a href=\"data-editor://World/Area\">INSERT AREAS!</a></p></body></html>", None, -1))

