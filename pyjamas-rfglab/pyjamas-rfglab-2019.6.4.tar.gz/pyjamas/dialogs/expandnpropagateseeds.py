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

from .expandseeds import ExpandSeedsDialog
from .propagateseeds import PropagateSeedsDialog


class ExpandNPropagateSeedsDialog(ExpandSeedsDialog, PropagateSeedsDialog):

    def __init__(self):
        super().__init__()

    def setupUi(self, Dialog, firstslice=None, lastslice=None, gaussian_sigma=None, xcorrwinsz=None):
        import pyjamas.rcallbacks as rcallbacks

        # Parameter error control.
        if ExpandNPropagateSeedsDialog.firstSlice < 0 and firstslice:
            ExpandNPropagateSeedsDialog.firstSlice = firstslice
        elif ExpandNPropagateSeedsDialog.firstSlice < 0:
            ExpandNPropagateSeedsDialog.firstSlice = 0

        if ExpandNPropagateSeedsDialog.lastSlice < 0 and lastslice:
            ExpandNPropagateSeedsDialog.lastSlice = lastslice
        elif ExpandNPropagateSeedsDialog.lastSlice < 0:
            ExpandNPropagateSeedsDialog.lastSlice = 1

        if ExpandNPropagateSeedsDialog.gaussianSigma < 0:
            ExpandNPropagateSeedsDialog.gaussianSigma = rcallbacks.rcbsegment.RCBSegment.DEFAULT_SMOOTHING_SIGMA
        else:
            ExpandNPropagateSeedsDialog.gaussianSigma = gaussian_sigma

        if ExpandNPropagateSeedsDialog.window_size < 0:
            ExpandNPropagateSeedsDialog.window_size = rcallbacks.rcbsegment.RCBSegment.DEFAULT_WINDOW_SZ
        else:
            ExpandNPropagateSeedsDialog.window_size = xcorrwinsz


        Dialog.setObjectName("Dialog")
        Dialog.resize(210, 274)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-160, 230, 341, 32))
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
        self.groupBox_3.setGeometry(QtCore.QRect(20, 130, 171, 81))
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        self.label_3.setGeometry(QtCore.QRect(7, 25, 81, 24))
        self.label_3.setObjectName("label_3")
        self.leGaussianSigma = QtWidgets.QLineEdit(self.groupBox_3)
        self.leGaussianSigma.setGeometry(QtCore.QRect(96, 27, 41, 21))
        self.leGaussianSigma.setObjectName("leGaussianSigma")
        self.leGaussianSigma.setText(str(ExpandNPropagateSeedsDialog.gaussianSigma))
        self.sbXCorrWinSize = QtWidgets.QSpinBox(self.groupBox_3)
        self.sbXCorrWinSize.setGeometry(QtCore.QRect(95, 50, 48, 24))
        self.sbXCorrWinSize.setObjectName("sbXCorrWinSize")
        self.sbXCorrWinSize.setMinimum(ExpandNPropagateSeedsDialog.SMALLEST_WINDOW_SIZE)
        self.sbXCorrWinSize.setMaximum(ExpandNPropagateSeedsDialog.MAX_WINDOW_SIZE)
        self.sbXCorrWinSize.setValue(ExpandNPropagateSeedsDialog.window_size)
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setGeometry(QtCore.QRect(8, 50, 90, 24))
        self.label_4.setObjectName("label_4")

        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.buttonBox.accepted.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Expand & Propagate"))
        self.groupBox_2.setTitle(_translate("Dialog", "Slices"))
        self.label_2.setText(_translate("Dialog", "last slice"))
        self.label.setText(_translate("Dialog", "first slice"))
        self.groupBox_3.setTitle(_translate("Dialog", "Parameters"))
        self.label_3.setText(_translate("Dialog", "smoothing σ"))
        self.label_4.setText(_translate("Dialog", "xcorr window"))

    def parameters(self):
        ExpandNPropagateSeedsDialog.firstSlice = self.sbFirst.value()
        ExpandNPropagateSeedsDialog.lastSlice = self.sbLast.value()
        ExpandNPropagateSeedsDialog.gaussianSigma = float(self.leGaussianSigma.text())
        ExpandNPropagateSeedsDialog.window_size = self.sbXCorrWinSize.value()

        theparameters = {'first': ExpandNPropagateSeedsDialog.firstSlice, 'last': ExpandNPropagateSeedsDialog.lastSlice,
                         'sigma': ExpandNPropagateSeedsDialog.gaussianSigma,
                         'xcorr_win_sz': ExpandNPropagateSeedsDialog.window_size}

        return theparameters
