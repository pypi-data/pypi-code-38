# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/travis/build/randovania/randovania/randovania/gui/item_configuration_popup.ui',
# licensing of '/home/travis/build/randovania/randovania/randovania/gui/item_configuration_popup.ui' applies.
#
# Created: Fri Jun 14 21:12:31 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_ItemConfigurationPopup(object):
    def setupUi(self, ItemConfigurationPopup):
        ItemConfigurationPopup.setObjectName("ItemConfigurationPopup")
        ItemConfigurationPopup.resize(326, 228)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ItemConfigurationPopup.sizePolicy().hasHeightForWidth())
        ItemConfigurationPopup.setSizePolicy(sizePolicy)
        ItemConfigurationPopup.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout = QtWidgets.QVBoxLayout(ItemConfigurationPopup)
        self.verticalLayout.setObjectName("verticalLayout")
        self.warning_label = QtWidgets.QLabel(ItemConfigurationPopup)
        self.warning_label.setObjectName("warning_label")
        self.verticalLayout.addWidget(self.warning_label)
        self.included_box = QtWidgets.QGroupBox(ItemConfigurationPopup)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.included_box.sizePolicy().hasHeightForWidth())
        self.included_box.setSizePolicy(sizePolicy)
        self.included_box.setCheckable(True)
        self.included_box.setObjectName("included_box")
        self.gridLayout = QtWidgets.QGridLayout(self.included_box)
        self.gridLayout.setObjectName("gridLayout")
        self.shuffled_spinbox = QtWidgets.QSpinBox(self.included_box)
        self.shuffled_spinbox.setMinimum(1)
        self.shuffled_spinbox.setMaximum(99)
        self.shuffled_spinbox.setObjectName("shuffled_spinbox")
        self.gridLayout.addWidget(self.shuffled_spinbox, 2, 1, 1, 1)
        self.shuffled_radio = QtWidgets.QRadioButton(self.included_box)
        self.shuffled_radio.setObjectName("shuffled_radio")
        self.gridLayout.addWidget(self.shuffled_radio, 2, 0, 1, 1)
        self.starting_radio = QtWidgets.QRadioButton(self.included_box)
        self.starting_radio.setObjectName("starting_radio")
        self.gridLayout.addWidget(self.starting_radio, 1, 0, 1, 1)
        self.vanilla_radio = QtWidgets.QRadioButton(self.included_box)
        self.vanilla_radio.setObjectName("vanilla_radio")
        self.gridLayout.addWidget(self.vanilla_radio, 0, 0, 1, 1)
        self.provided_ammo_label = QtWidgets.QLabel(self.included_box)
        self.provided_ammo_label.setObjectName("provided_ammo_label")
        self.gridLayout.addWidget(self.provided_ammo_label, 3, 0, 1, 1)
        self.provided_ammo_spinbox = QtWidgets.QSpinBox(self.included_box)
        self.provided_ammo_spinbox.setObjectName("provided_ammo_spinbox")
        self.gridLayout.addWidget(self.provided_ammo_spinbox, 3, 1, 1, 1)
        self.verticalLayout.addWidget(self.included_box)
        self.button_box = QtWidgets.QDialogButtonBox(ItemConfigurationPopup)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.button_box.setObjectName("button_box")
        self.verticalLayout.addWidget(self.button_box)

        self.retranslateUi(ItemConfigurationPopup)
        QtCore.QMetaObject.connectSlotsByName(ItemConfigurationPopup)

    def retranslateUi(self, ItemConfigurationPopup):
        ItemConfigurationPopup.setWindowTitle(QtWidgets.QApplication.translate("ItemConfigurationPopup", "Item Configuration", None, -1))
        self.warning_label.setText(QtWidgets.QApplication.translate("ItemConfigurationPopup", "Hidden warning!", None, -1))
        self.included_box.setTitle(QtWidgets.QApplication.translate("ItemConfigurationPopup", "Included", None, -1))
        self.shuffled_radio.setText(QtWidgets.QApplication.translate("ItemConfigurationPopup", "Shuffled", None, -1))
        self.starting_radio.setText(QtWidgets.QApplication.translate("ItemConfigurationPopup", "Starting Item", None, -1))
        self.vanilla_radio.setText(QtWidgets.QApplication.translate("ItemConfigurationPopup", "Vanilla", None, -1))
        self.provided_ammo_label.setToolTip(QtWidgets.QApplication.translate("ItemConfigurationPopup", "<html><head/><body><p>When this item is collected, it also gives this amount of the given ammos.</p><p>This is included in the calculation of how much each pickup of this ammo gives.</p></body></html>", None, -1))
        self.provided_ammo_label.setText(QtWidgets.QApplication.translate("ItemConfigurationPopup", "<html><head/><body><p>Provided Ammo</p><p>(XXXX and YYYY)</p></body></html>", None, -1))

