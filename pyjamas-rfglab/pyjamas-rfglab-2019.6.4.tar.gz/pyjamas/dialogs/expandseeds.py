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

from PyQt5 import QtCore, QtWidgets


class ExpandSeedsDialog(object):
    # These are class variables so that, when their values change, they change, and next time the same dialog is
    # open, the most recent values are preserved.
    firstSlice = -1
    lastSlice = -1
    gaussianSigma = -1.

    def __init__(self):
        super().__init__()

    def setupUi(self, Dialog, firstslice=None, lastslice=None, gaussian_sigma=None):
        import pyjamas.rcallbacks as rcallbacks

        # Parameter error control.
        if ExpandSeedsDialog.firstSlice < 0 and firstslice:
            ExpandSeedsDialog.firstSlice = firstslice
        elif ExpandSeedsDialog.firstSlice < 0:
            ExpandSeedsDialog.firstSlice = 0

        if ExpandSeedsDialog.lastSlice < 0 and lastslice:
            ExpandSeedsDialog.lastSlice = lastslice
        elif ExpandSeedsDialog.lastSlice < 0:
            ExpandSeedsDialog.lastSlice = 1

        if ExpandSeedsDialog.gaussianSigma < 0:
            ExpandSeedsDialog.gaussianSigma = rcallbacks.rcbsegment.RCBSegment.DEFAULT_SMOOTHING_SIGMA
        else:
            ExpandSeedsDialog.gaussianSigma = gaussian_sigma

        Dialog.setObjectName("Dialog")
        Dialog.resize(210, 260)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-160, 210, 341, 32))
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
        self.sbLast.setValue(firstslice)
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
        self.groupBox_3 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_3.setGeometry(QtCore.QRect(20, 130, 171, 61))
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        self.label_3.setGeometry(QtCore.QRect(7, 25, 81, 24))
        self.label_3.setObjectName("label_3")
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit.setGeometry(QtCore.QRect(96, 27, 41, 21))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setText(str(ExpandSeedsDialog.gaussianSigma))

        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.buttonBox.accepted.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Expand seeds"))
        self.groupBox_2.setTitle(_translate("Dialog", "Slices"))
        self.label_2.setText(_translate("Dialog", "last slice"))
        self.label.setText(_translate("Dialog", "first slice"))
        self.groupBox_3.setTitle(_translate("Dialog", "Parameters"))
        self.label_3.setText(_translate("Dialog", "smoothing σ"))

    def parameters(self):
        ExpandSeedsDialog.firstSlice = self.sbFirst.value()
        ExpandSeedsDialog.lastSlice = self.sbLast.value()
        ExpandSeedsDialog.gaussianSigma = float(self.lineEdit.text())

        theparameters = {'first': ExpandSeedsDialog.firstSlice, 'last': ExpandSeedsDialog.lastSlice,
                         'sigma': ExpandSeedsDialog.gaussianSigma}

        return theparameters
