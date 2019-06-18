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


class PropagateSeedsDialog(object):

    SMALLEST_WINDOW_SIZE = 3
    MAX_WINDOW_SIZE = 512

    # These are class variables so that, when their values change, they change, and next time the same dialog is
    # open, the most recent values are preserved.
    firstSlice = -1
    lastSlice = -1
    window_size = -1
    gradientFlag = False

    def __init__(self):
        super().__init__()


    def setupUi(self, Dialog, firstslice=None, lastslice=None, xcorrwinsz=None):
        import pyjamas.rcallbacks as rcallbacks

        # Parameter error control.
        if PropagateSeedsDialog.firstSlice < 0 and firstslice:
            PropagateSeedsDialog.firstSlice = firstslice
        elif PropagateSeedsDialog.firstSlice < 0:
            PropagateSeedsDialog.firstSlice = 0

        if PropagateSeedsDialog.lastSlice < 0 and lastslice:
            PropagateSeedsDialog.lastSlice = lastslice
        elif PropagateSeedsDialog.lastSlice < 0:
            PropagateSeedsDialog.lastSlice = 1

        if PropagateSeedsDialog.window_size < 0:
            PropagateSeedsDialog.window_size = rcallbacks.rcbsegment.RCBSegment.DEFAULT_WINDOW_SZ
        else:
            PropagateSeedsDialog.window_size = xcorrwinsz

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
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 20, 171, 101))
        self.groupBox_2.setObjectName("groupBox_2")
        self.sbLast = QtWidgets.QSpinBox(self.groupBox_2)
        self.sbLast.setGeometry(QtCore.QRect(95, 70, 48, 24))
        self.sbLast.setMinimum(1)
        self.sbLast.setMaximum(lastslice)
        self.sbLast.setValue(firstslice+1)
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
        self.label_3.setGeometry(QtCore.QRect(8, 24, 81, 24))
        self.label_3.setObjectName("label_3")
        self.sbXcorrWindowSz = QtWidgets.QSpinBox(self.groupBox_3)
        self.sbXcorrWindowSz.setGeometry(QtCore.QRect(97, 24, 48, 24))
        self.sbXcorrWindowSz.setObjectName("sbXcorrWindowSz")
        self.sbXcorrWindowSz.setMinimum(PropagateSeedsDialog.SMALLEST_WINDOW_SIZE)
        self.sbXcorrWindowSz.setMaximum(PropagateSeedsDialog.MAX_WINDOW_SIZE)
        self.sbXcorrWindowSz.setValue(PropagateSeedsDialog.window_size)

        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.buttonBox.accepted.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Propagate seeds"))
        self.groupBox_2.setTitle(_translate("Dialog", "Slices"))
        self.label_2.setText(_translate("Dialog", "last slice"))
        self.label.setText(_translate("Dialog", "first slice"))
        self.groupBox_3.setTitle(_translate("Dialog", "Parameters"))
        self.label_3.setText(_translate("Dialog", "xcorr window"))

    def parameters(self):
        PropagateSeedsDialog.firstSlice = self.sbFirst.value()
        PropagateSeedsDialog.lastSlice = self.sbLast.value()
        PropagateSeedsDialog.window_size = self.sbXcorrWindowSz.value()

        theparameters = {'first': PropagateSeedsDialog.firstSlice, 'last': PropagateSeedsDialog.lastSlice, 'xcorr_win_sz': PropagateSeedsDialog.window_size}

        return theparameters
