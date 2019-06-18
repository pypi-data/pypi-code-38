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

from PyQt5 import QtCore, QtGui, QtWidgets

class MeasurePolyDialog(object):
    # todo: change measurement options to be morphology and intensity.

    # These are class variables so that, when their values change, they change, and next time the same dialog is
    # open, the most recent values are preserved.
    savepath = None
    firstSlice = -1
    lastSlice = -1
    area = True
    perimeter = True
    pixels = True
    image = True

    def __init__(self):
        super().__init__()

    def setupUi(self, Dialog, savepath=None, firstslice=None, lastslice=None):
        # Parameter error control.
        if MeasurePolyDialog.firstSlice < 0 and firstslice:
            MeasurePolyDialog.firstSlice = firstslice
        elif MeasurePolyDialog.firstSlice < 0:
            MeasurePolyDialog.firstSlice = 0

        if MeasurePolyDialog.lastSlice < 0 and lastslice:
            MeasurePolyDialog.lastSlice = lastslice
        elif MeasurePolyDialog.lastSlice < 0:
            MeasurePolyDialog.lastSlice = 1

        if MeasurePolyDialog.savepath == '' and savepath:
            MeasurePolyDialog.savepath = savepath

        Dialog.setObjectName("Dialog")
        Dialog.resize(412, 253)
        Dialog.setFont(QtGui.QFont("Arial", 12))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 210, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(30, 20, 148, 171))
        self.groupBox.setObjectName("groupBox")
        self.cbImStats = QtWidgets.QCheckBox(self.groupBox)
        self.cbImStats.setGeometry(QtCore.QRect(10, 130, 151, 20))
        self.cbImStats.setChecked(MeasurePolyDialog.image)
        self.cbImStats.setObjectName("checkBox_4")
        self.cbPerim = QtWidgets.QCheckBox(self.groupBox)
        self.cbPerim.setGeometry(QtCore.QRect(10, 62, 151, 20))
        self.cbPerim.setChecked(MeasurePolyDialog.perimeter)
        self.cbPerim.setObjectName("cbPerim")
        self.cbArea = QtWidgets.QCheckBox(self.groupBox)
        self.cbArea.setGeometry(QtCore.QRect(10, 28, 151, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbArea.sizePolicy().hasHeightForWidth())
        self.cbArea.setSizePolicy(sizePolicy)
        self.cbArea.setChecked(MeasurePolyDialog.area)
        self.cbArea.setObjectName("cbArea")
        self.cbPixVal = QtWidgets.QCheckBox(self.groupBox)
        self.cbPixVal.setGeometry(QtCore.QRect(10, 96, 151, 20))
        self.cbPixVal.setChecked(MeasurePolyDialog.pixels)
        self.cbPixVal.setObjectName("cbPixVal")
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(210, 20, 171, 101))
        self.groupBox_2.setObjectName("groupBox_2")
        self.sbLast = QtWidgets.QSpinBox(self.groupBox_2)
        self.sbLast.setGeometry(QtCore.QRect(95, 70, 48, 24))
        self.sbLast.setMinimum(1)
        self.sbLast.setMaximum(lastslice)
        self.sbLast.setValue(MeasurePolyDialog.lastSlice)
        self.sbLast.setObjectName("sbLast")
        self.sbFirst = QtWidgets.QSpinBox(self.groupBox_2)
        self.sbFirst.setGeometry(QtCore.QRect(95, 26, 48, 24))
        self.sbFirst.setMinimum(1)
        self.sbFirst.setMaximum(lastslice)
        self.sbFirst.setValue(MeasurePolyDialog.firstSlice)
        self.sbFirst.setObjectName("sbFirst")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(34, 70, 53, 24))
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(31, 26, 56, 24))
        self.label.setObjectName("label")
        self.groupBox_3 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_3.setGeometry(QtCore.QRect(210, 130, 171, 61))
        self.groupBox_3.setObjectName("groupBox_3")
        self.btnSaveFile = QtWidgets.QToolButton(self.groupBox_3)
        self.btnSaveFile.setGeometry(QtCore.QRect(130, 28, 26, 22))
        self.btnSaveFile.setObjectName("btn_input_folder")
        self.btnSaveFile.clicked.connect(self.openSaveFileDialog) # Adding functionality to the button.
        self.editFilename = QtWidgets.QPlainTextEdit(self.groupBox_3)
        self.editFilename.setGeometry(QtCore.QRect(10, 30, 111, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.editFilename.sizePolicy().hasHeightForWidth())
        self.editFilename.setSizePolicy(sizePolicy)
        self.editFilename.setMaximumSize(QtCore.QSize(16777215, 20))
        self.editFilename.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.editFilename.setPlainText(MeasurePolyDialog.savepath)
        self.editFilename.setObjectName("editFilename")
        self.buttonBox.raise_()
        self.label.raise_()
        self.groupBox.raise_()
        self.groupBox_2.raise_()
        self.label_2.raise_()
        self.label.raise_()
        self.groupBox_3.raise_()

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Measure polylines"))
        self.groupBox.setTitle(_translate("Dialog", "Measurements"))
        self.cbImStats.setText(_translate("Dialog", "image stats"))
        self.cbPerim.setText(_translate("Dialog", "perimeter"))
        self.cbArea.setText(_translate("Dialog", "area"))
        self.cbPixVal.setText(_translate("Dialog", "pixel values"))
        self.groupBox_2.setTitle(_translate("Dialog", "Slices to measure"))
        self.label_2.setText(_translate("Dialog", "last slice"))
        self.label.setText(_translate("Dialog", "first slice"))
        self.groupBox_3.setTitle(_translate("Dialog", "Save to"))
        self.btnSaveFile.setText(_translate("Dialog", "..."))

    def openSaveFileDialog(self):
        fname = QtWidgets.QFileDialog.getSaveFileName(None, 'Save measurements ...', MeasurePolyDialog.savepath,
                                                      filter='CSV (*.csv)')

        self.editFilename.setPlainText(fname[0])

    def measurements(self) -> dict:
        MeasurePolyDialog.savepath = self.editFilename.toPlainText()
        MeasurePolyDialog.firstSlice = self.sbFirst.value()
        MeasurePolyDialog.lastSlice = self.sbLast.value()
        MeasurePolyDialog.area = bool(self.cbArea.isChecked())
        MeasurePolyDialog.perimeter = bool(self.cbPerim.isChecked())
        MeasurePolyDialog.pixels = bool(self.cbPixVal.isChecked())
        MeasurePolyDialog.image = bool(self.cbImStats.isChecked())

        themeasurements = {'path': MeasurePolyDialog.savepath, 'first': MeasurePolyDialog.firstSlice, 'last': MeasurePolyDialog.lastSlice, 'area': MeasurePolyDialog.area, 'perimeter': MeasurePolyDialog.perimeter, 'pixels': MeasurePolyDialog.pixels, 'image': MeasurePolyDialog.image}

        return themeasurements

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = MeasurePolyDialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

