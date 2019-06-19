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

import pyjamas.rimage.rimclassifier.rimsvm as rimsvm
import pyjamas.rutils as rutils


class SVMDialog(object):
    positive_training_folder: str = ''
    negative_training_folder: str = ''
    hard_negative_training_folder: str = ''
    train_image_size: Tuple[int, int] = (0, 0)
    step_sz: Tuple[int, int] = rimsvm.svm.DEFAULT_STEP_SZ
    histogram_of_gradients: bool = True
    misclass_penalty_C: float = rimsvm.svm.DEFAULT_C
    kernel_type: int = rimsvm.svm.DEFAULT_KERNEL_TYPE

    def __init__(self):
        super().__init__()

    def setupUi(self, SVM, parameters: dict = None):
        if parameters is None or parameters is False:
            parameters = {
                'positive_training_folder': SVMDialog.positive_training_folder,
                'negative_training_folder': SVMDialog.negative_training_folder,
                'hard_negative_training_folder': SVMDialog.hard_negative_training_folder,
                'histogram_of_gradients': SVMDialog.histogram_of_gradients,
                'train_image_size': SVMDialog.train_image_size,
                'step_sz': SVMDialog.step_sz,
                'misclass_penalty_C': SVMDialog.misclass_penalty_C,
                'kernel_type': SVMDialog.kernel_type,
            }

        SVMDialog.positive_training_folder = parameters.get('positive_training_folder', SVMDialog.positive_training_folder)
        SVMDialog.negative_training_folder = parameters.get('negative_training_folder', SVMDialog.negative_training_folder)
        SVMDialog.hard_negative_training_folder = parameters.get('hard_negative_training_folder', SVMDialog.hard_negative_training_folder)
        SVMDialog.histogram_of_gradients = parameters.get('histogram_of_gradients', SVMDialog.histogram_of_gradients)
        SVMDialog.train_image_size = parameters.get('train_image_size', SVMDialog.train_image_size)
        SVMDialog.step_sz = parameters.get('step_sz', SVMDialog.step_sz)
        SVMDialog.misclass_penalty_C = parameters.get('misclass_penalty_C', SVMDialog.misclass_penalty_C)
        SVMDialog.kernel_type = parameters.get('kernel_type', SVMDialog.kernel_type)

        SVM.setObjectName("SVM")
        SVM.resize(614, 432)
        self.buttonBox = QtWidgets.QDialogButtonBox(SVM)
        self.buttonBox.setGeometry(QtCore.QRect(240, 374, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox_2 = QtWidgets.QGroupBox(SVM)
        self.groupBox_2.setGeometry(QtCore.QRect(30, 26, 551, 121))
        self.groupBox_2.setObjectName("groupBox_2")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(31, 26, 141, 24))
        self.label.setObjectName("label")
        self.positive_training_folder_edit = QtWidgets.QLineEdit(self.groupBox_2)
        self.positive_training_folder_edit.setGeometry(QtCore.QRect(220, 30, 261, 21))
        self.positive_training_folder_edit.setObjectName("positive_training_folder_edit")
        self.positive_training_folder_edit.setText(SVMDialog.positive_training_folder)
        self.btnSavePositive = QtWidgets.QToolButton(self.groupBox_2)
        self.btnSavePositive.setGeometry(QtCore.QRect(490, 30, 26, 22))
        self.btnSavePositive.setObjectName("btnSavePositive")
        self.btnSavePositive.clicked.connect(self._open_positive_folder_dialog)
        self.negative_training_folder_edit = QtWidgets.QLineEdit(self.groupBox_2)
        self.negative_training_folder_edit.setGeometry(QtCore.QRect(220, 60, 261, 21))
        self.negative_training_folder_edit.setObjectName("negative_training_folder_edit")
        self.negative_training_folder_edit.setText(SVMDialog.negative_training_folder)
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(31, 56, 141, 24))
        self.label_2.setObjectName("label_2")
        self.btnSaveNegative = QtWidgets.QToolButton(self.groupBox_2)
        self.btnSaveNegative.setGeometry(QtCore.QRect(490, 60, 26, 22))
        self.btnSaveNegative.setObjectName("btnSaveNegative")
        self.btnSaveNegative.clicked.connect(self._open_negative_folder_dialog)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(31, 86, 181, 24))
        self.label_3.setObjectName("label_3")
        self.btnSaveHard = QtWidgets.QToolButton(self.groupBox_2)
        self.btnSaveHard.setGeometry(QtCore.QRect(490, 90, 26, 22))
        self.btnSaveHard.setObjectName("btnSaveHard")
        self.btnSaveHard.clicked.connect(self._open_hard_folder_dialog)
        self.hard_negative_training_folder_edit = QtWidgets.QLineEdit(self.groupBox_2)
        self.hard_negative_training_folder_edit.setGeometry(QtCore.QRect(220, 90, 261, 21))
        self.hard_negative_training_folder_edit.setObjectName("hard_negative_training_folder_edit")
        self.hard_negative_training_folder_edit.setText(SVMDialog.hard_negative_training_folder)
        self.groupBox_3 = QtWidgets.QGroupBox(SVM)
        self.groupBox_3.setGeometry(QtCore.QRect(30, 156, 251, 61))
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setGeometry(QtCore.QRect(31, 28, 141, 24))
        self.label_4.setObjectName("label_4")
        self.lnWidth = QtWidgets.QLineEdit(self.groupBox_3)
        self.lnWidth.setGeometry(QtCore.QRect(70, 30, 31, 21))
        self.lnWidth.setObjectName("lnWidth")
        self.lnWidth.setText(str(SVMDialog.train_image_size[1]))
        self.lnHeight = QtWidgets.QLineEdit(self.groupBox_3)
        self.lnHeight.setGeometry(QtCore.QRect(170, 30, 31, 21))
        self.lnHeight.setObjectName("lnHeight")
        self.lnHeight.setText(str(SVMDialog.train_image_size[0]))
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setGeometry(QtCore.QRect(120, 28, 141, 24))
        self.label_5.setObjectName("label_5")
        self.label_5.raise_()
        self.label_4.raise_()
        self.lnWidth.raise_()
        self.lnHeight.raise_()
        self.groupBox_4 = QtWidgets.QGroupBox(SVM)
        self.groupBox_4.setGeometry(QtCore.QRect(30, 226, 551, 61))
        self.groupBox_4.setObjectName("groupBox_4")
        self.checkBoxHOG = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBoxHOG.setGeometry(QtCore.QRect(30, 30, 161, 20))
        self.checkBoxHOG.setObjectName("checkBoxHOG")
        self.checkBoxHOG.setChecked(SVMDialog.histogram_of_gradients)
        self.groupBox_5 = QtWidgets.QGroupBox(SVM)
        self.groupBox_5.setGeometry(QtCore.QRect(30, 296, 551, 61))
        self.groupBox_5.setObjectName("groupBox_5")
        self.lnC = QtWidgets.QLineEdit(self.groupBox_5)
        self.lnC.setGeometry(QtCore.QRect(210, 30, 31, 21))
        self.lnC.setObjectName("lnC")
        self.lnC.setText(str(SVMDialog.misclass_penalty_C))
        self.label_8 = QtWidgets.QLabel(self.groupBox_5)
        self.label_8.setGeometry(QtCore.QRect(30, 28, 181, 24))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.groupBox_5)
        self.label_9.setGeometry(QtCore.QRect(263, 27, 141, 24))
        self.label_9.setObjectName("label_9")
        self.comboKernel = QtWidgets.QComboBox(self.groupBox_5)
        self.comboKernel.setGeometry(QtCore.QRect(310, 28, 104, 26))
        self.comboKernel.setObjectName("comboKernel")
        for ii, _ in enumerate(rimsvm.svm.KERNEL_TYPES):
            self.comboKernel.addItem("")
        self.comboKernel.setCurrentIndex(SVMDialog.kernel_type)
        self.label_8.raise_()
        self.lnC.raise_()
        self.label_9.raise_()
        self.comboKernel.raise_()
        self.groupBox_6 = QtWidgets.QGroupBox(SVM)
        self.groupBox_6.setGeometry(QtCore.QRect(300, 155, 281, 61))
        self.groupBox_6.setObjectName("groupBox_6")
        self.label_12 = QtWidgets.QLabel(self.groupBox_6)
        self.label_12.setGeometry(QtCore.QRect(31, 28, 141, 24))
        self.label_12.setObjectName("label_12")
        self.lnRow = QtWidgets.QLineEdit(self.groupBox_6)
        self.lnRow.setGeometry(QtCore.QRect(70, 30, 31, 21))
        self.lnRow.setObjectName("lnRow")
        self.lnRow.setText(str(SVMDialog.step_sz[0]))
        self.lnColumn = QtWidgets.QLineEdit(self.groupBox_6)
        self.lnColumn.setGeometry(QtCore.QRect(180, 30, 31, 21))
        self.lnColumn.setObjectName("lnColumn")
        self.lnColumn.setText(str(SVMDialog.step_sz[1]))
        self.label_13 = QtWidgets.QLabel(self.groupBox_6)
        self.label_13.setGeometry(QtCore.QRect(120, 28, 141, 24))
        self.label_13.setObjectName("label_13")
        self.label_13.raise_()
        self.label_12.raise_()
        self.lnRow.raise_()
        self.lnColumn.raise_()

        self.retranslateUi(SVM)
        self.buttonBox.accepted.connect(SVM.accept)
        self.buttonBox.rejected.connect(SVM.reject)
        QtCore.QMetaObject.connectSlotsByName(SVM)

    def retranslateUi(self, SVM):
        _translate = QtCore.QCoreApplication.translate
        SVM.setWindowTitle(_translate("SVM", "Train support vector machine"))
        self.groupBox_2.setTitle(_translate("SVM", "Project files"))
        self.label.setText(_translate("SVM", "positive training folder"))
        self.btnSavePositive.setText(_translate("SVM", "..."))
        self.label_2.setText(_translate("SVM", "negative training folder"))
        self.btnSaveNegative.setText(_translate("SVM", "..."))
        self.label_3.setText(_translate("SVM", "hard negative training folder"))
        self.btnSaveHard.setText(_translate("SVM", "..."))
        self.groupBox_3.setTitle(_translate("SVM", "Training image size"))
        self.label_4.setText(_translate("SVM", "width"))
        self.label_5.setText(_translate("SVM", "height"))
        self.groupBox_4.setTitle(_translate("SVM", "Image features"))
        self.checkBoxHOG.setText(_translate("SVM", "histogram of gradients"))
        self.groupBox_5.setTitle(_translate("SVM", "SVM parameters"))
        self.label_8.setText(_translate("SVM", "C (misclassification penalty)"))
        self.label_9.setText(_translate("SVM", "kernel"))
        self.groupBox_6.setTitle(_translate("SVM", "Image step size"))
        self.label_12.setText(_translate("SVM", "rows"))
        self.label_13.setText(_translate("SVM", "columns"))

        for ii, a_kernel in enumerate(rimsvm.svm.KERNEL_TYPES):
            self.comboKernel.setItemText(ii, _translate("SVM", a_kernel))

    def parameters(self) -> dict:
        SVMDialog.positive_training_folder = self.positive_training_folder_edit.text()
        SVMDialog.negative_training_folder = self.negative_training_folder_edit.text()
        SVMDialog.hard_negative_training_folder = self.hard_negative_training_folder_edit.text()
        SVMDialog.histogram_of_gradients = self.checkBoxHOG.isChecked()
        SVMDialog.train_image_size = int(self.lnHeight.text()), int(self.lnWidth.text())

        theparameters = {'positive_training_folder': SVMDialog.positive_training_folder,
                         'negative_training_folder': SVMDialog.negative_training_folder,
                         'hard_negative_training_folder': SVMDialog.hard_negative_training_folder,
                         'histogram_of_gradients': SVMDialog.histogram_of_gradients,
                         'train_image_size': SVMDialog.train_image_size,
                         'step_sz': SVMDialog.step_sz,
                         'misclass_penalty_C': SVMDialog.misclass_penalty_C,
                         'kernel_type': SVMDialog.kernel_type}

        return theparameters

    def _open_positive_folder_dialog(self) -> bool:
        folder = rutils.RUtils.open_folder_dialog("Negative training folder", SVMDialog.positive_training_folder)

        if folder == '' or folder is False:
            return False

        self.positive_training_folder_edit.setText(folder)

    def _open_negative_folder_dialog(self) -> bool:
        folder = rutils.RUtils.open_folder_dialog("Negative training folder", SVMDialog.negative_training_folder)

        if folder == '' or folder is False:
            return False

        self.negative_training_folder_edit.setText(folder)

    def _open_hard_folder_dialog(self) -> bool:
        folder = rutils.RUtils.open_folder_dialog("Negative training folder", SVMDialog.hard_negative_training_folder)

        if folder == '' or folder is False:
            return False

        self.hard_negative_training_folder_edit.setText(folder)

