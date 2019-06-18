"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import Tuple

from PyQt5 import QtCore, QtWidgets


class TimePointsDialog(object):
    # These are class variables so that, when their values change, they change, and next time the same dialog is
    # open, the most recent values are preserved.
    firstSlice: int = -1
    lastSlice: int = -1

    def __init__(self):
        super().__init__()

    def setupUi(self, Dialog, firstslice: int = None, lastslice: int = None):
        # Parameter error control.
        if firstslice < 1 and TimePointsDialog.firstSlice >= 1:
            firstslice = TimePointsDialog.firstSlice
        elif firstslice < 1 and TimePointsDialog.firstSlice < 1:
            firstslice = 1

        if lastslice < 1 and TimePointsDialog.lastSlice >= 1:
            lastslice = TimePointsDialog.lastSlice
        elif lastslice < 1 and TimePointsDialog.lastSlice < 1:
            lastslice = 1

        Dialog.setObjectName("Dialog")
        Dialog.resize(210, 178)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-160, 130, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 20, 171, 101))
        self.groupBox_2.setObjectName("groupBox_2")
        self.sbLast = QtWidgets.QSpinBox(self.groupBox_2)
        self.sbLast.setGeometry(QtCore.QRect(95, 70, 48, 24))
        self.sbLast.setMinimum(1)
        self.sbLast.setMaximum(lastslice)
        self.sbLast.setValue(lastslice)
        self.sbLast.setObjectName("sbLast")
        self.sbFirst = QtWidgets.QSpinBox(self.groupBox_2)
        self.sbFirst.setGeometry(QtCore.QRect(95, 26, 48, 24))
        self.sbFirst.setMinimum(1)
        self.sbFirst.setMaximum(lastslice)
        self.sbFirst.setValue(firstslice)
        self.sbFirst.setObjectName("sbFirst")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(34, 70, 53, 24))
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(31, 26, 56, 24))
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.buttonBox.accepted.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Select time points"))
        self.groupBox_2.setTitle(_translate("Dialog", "Slices"))
        self.label_2.setText(_translate("Dialog", "last slice"))
        self.label.setText(_translate("Dialog", "first slice"))

    def parameters(self) -> Tuple[int, int]:
        TimePointsDialog.firstSlice = self.sbFirst.value()
        TimePointsDialog.lastSlice = self.sbLast.value()

        return TimePointsDialog.firstSlice, TimePointsDialog.lastSlice