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

import os

from PyQt5 import QtCore, QtWidgets

import pyjamas.rutils as rutils


class BatchProjectConcatenateDialog():
    input_folder_name_classvar: str = '.'
    slice_list_str_classvar: str = ''
    file_name_classvar: str = ''

    def __init__(self):
        super().__init__()

    def setupUi(self, Dialog, input_folder: str = None, slices: str = None, output_file: str = None):
        if input_folder and os.path.exists(input_folder):
            BatchProjectConcatenateDialog.input_folder_name_classvar = input_folder

        if slices:
            BatchProjectConcatenateDialog.slice_list_str_classvar = slices

        if output_file:
            BatchProjectConcatenateDialog.file_name_classvar = output_file

        Dialog.setObjectName("Dialog")
        Dialog.resize(342, 183)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-87, 140, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.input_folder_name = QtWidgets.QLineEdit(Dialog)
        self.input_folder_name.setGeometry(QtCore.QRect(204, 20, 113, 21))
        self.input_folder_name.setObjectName("input_folder_name")
        self.input_folder_name.setText(os.path.abspath(BatchProjectConcatenateDialog.input_folder_name_classvar))
        self.input_slices = QtWidgets.QLineEdit(Dialog)
        self.input_slices.setGeometry(QtCore.QRect(204, 60, 113, 21))
        self.input_slices.setObjectName("input_slices")
        self.input_slices.setText(BatchProjectConcatenateDialog.slice_list_str_classvar)
        self.input_file_name = QtWidgets.QLineEdit(Dialog)
        self.input_file_name.setGeometry(QtCore.QRect(204, 98, 113, 21))
        self.input_file_name.setObjectName("input_file_name")
        self.input_file_name.setText(BatchProjectConcatenateDialog.file_name_classvar)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(25, 23, 81, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(25, 63, 151, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(25, 102, 151, 16))
        self.label_3.setObjectName("label_3")
        self.btn_input_folder = QtWidgets.QToolButton(Dialog)
        self.btn_input_folder.setGeometry(QtCore.QRect(175, 20, 26, 22))
        self.btn_input_folder.setObjectName("btn_input_folder")
        self.btn_input_folder.clicked.connect(self._open_folder_dialog)

        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.buttonBox.accepted.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Project and concatenate"))
        self.label.setText(_translate("Dialog", "input folder"))
        self.label_2.setText(_translate("Dialog", "slices (e.g. \'0, 3-4, 20\')"))
        self.label_3.setText(_translate("Dialog", "output file name"))
        self.btn_input_folder.setText(_translate("Dialog", "..."))

    def parameters(self) -> dict:
        BatchProjectConcatenateDialog.input_folder_name_classvar = self.input_folder_name.text()
        BatchProjectConcatenateDialog.slice_list_str_classvar = self.input_slices.text()
        BatchProjectConcatenateDialog.file_name_classvar = self.input_file_name.text()

        theparameters = {'input_folder': BatchProjectConcatenateDialog.input_folder_name_classvar,
                         'slice_list': BatchProjectConcatenateDialog.slice_list_str_classvar,
                         'file_name': BatchProjectConcatenateDialog.file_name_classvar}

        return theparameters

    def _open_folder_dialog(self) -> bool:
        folder = rutils.RUtils.open_folder_dialog("Input folder", BatchProjectConcatenateDialog.input_folder_name_classvar)

        if folder == '' or folder is False:
            return False

        self.input_folder_name.setText(folder)
