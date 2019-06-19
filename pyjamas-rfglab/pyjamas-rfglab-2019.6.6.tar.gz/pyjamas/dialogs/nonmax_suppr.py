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

from functools import partial

from PyQt5 import QtCore, QtWidgets

from pyjamas.pjscore import PyJAMAS
from pyjamas.rimage.rimclassifier.rimclassifier import rimclassifier


class NonMaxDialog(object):
    max_num_objects: int = rimclassifier.DEFAULT_MAX_NUM_OBJECTS
    prob_threshold: float = rimclassifier.DEFAULT_PROB_THRESHOLD
    iou_threshold: float = rimclassifier.DEFAULT_IOU_THRESHOLD

    MAX_POSSIBLE_NUMBER_OBJECTS: int = 2000
    MAX_POSSIBLE_IOU_THRESHOLD: float = 1.0

    def __init__(self, pjs: PyJAMAS):
        super().__init__()
        self.pjs = pjs

    def setupUi(self, Dialog, max_num_objects_arg: int = None, prob_threshold_arg: float = None, iou_threshold_arg: float = None):
        if max_num_objects_arg and max_num_objects_arg > 0:
            NonMaxDialog.max_num_objects = max_num_objects_arg

        if prob_threshold_arg and 0. <= prob_threshold_arg <= 1.:
            NonMaxDialog.prob_threshold = prob_threshold_arg

        if iou_threshold_arg and iou_threshold_arg >= 0:
            NonMaxDialog.iou_threshold = iou_threshold_arg

        self.Dialog = Dialog
        self.Dialog.setObjectName("Dialog")
        self.Dialog.resize(304, 234)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-60, 193, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.max_num_objects_dial = QtWidgets.QDial(self.Dialog)
        self.max_num_objects_dial.setGeometry(QtCore.QRect(195, 4, 50, 64))
        self.max_num_objects_dial.setObjectName("max_num_objects_dial")
        self.max_num_objects_dial.setMinimum(1)
        self.max_num_objects_dial.setMaximum(NonMaxDialog.MAX_POSSIBLE_NUMBER_OBJECTS)
        self.max_num_objects_dial.setValue(NonMaxDialog.max_num_objects)
        self.prob_threshold_dial = QtWidgets.QDial(self.Dialog)
        self.prob_threshold_dial.setGeometry(QtCore.QRect(195, 64, 50, 64))
        self.prob_threshold_dial.setObjectName("prob_threshold")
        self.prob_threshold_dial.setMinimum(0)
        self.prob_threshold_dial.setMaximum(100)
        self.prob_threshold_dial.setValue(NonMaxDialog.prob_threshold*100)
        self.iou_threshold_dial = QtWidgets.QDial(self.Dialog)
        self.iou_threshold_dial.setGeometry(QtCore.QRect(195, 124, 50, 64))
        self.iou_threshold_dial.setObjectName("iou_threshold")
        self.iou_threshold_dial.setMinimum(0)
        self.iou_threshold_dial.setMaximum(NonMaxDialog.MAX_POSSIBLE_IOU_THRESHOLD*100)
        self.iou_threshold_dial.setValue(NonMaxDialog.iou_threshold*100)
        self.label_8 = QtWidgets.QLabel(self.Dialog)
        self.label_8.setGeometry(QtCore.QRect(13, 24, 181, 24))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.Dialog)
        self.label_9.setGeometry(QtCore.QRect(13, 84, 181, 24))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.Dialog)
        self.label_10.setGeometry(QtCore.QRect(13, 144, 181, 24))
        self.label_10.setObjectName("label_10")
        self.label_numobj = QtWidgets.QLabel(self.Dialog)
        self.label_numobj.setGeometry(QtCore.QRect(250, 26, 181, 24))
        self.label_numobj.setObjectName("label_8")
        self.label_numobj.setText(str(self.max_num_objects_dial.value()))
        self.label_prob = QtWidgets.QLabel(self.Dialog)
        self.label_prob.setGeometry(QtCore.QRect(250, 86, 181, 24))
        self.label_prob.setObjectName("label_9")
        self.label_prob.setText(str(self.prob_threshold_dial.value() / 100.))
        self.label_iou = QtWidgets.QLabel(self.Dialog)
        self.label_iou.setGeometry(QtCore.QRect(250, 146, 181, 24))
        self.label_iou.setObjectName("label_10")
        self.label_iou.setText(str(self.iou_threshold_dial.value() / 100.))


        self.retranslateUi()
        self.buttonBox.accepted.connect(self.Dialog.accept)
        self.buttonBox.rejected.connect(self.Dialog.reject)
        self.max_num_objects_dial.valueChanged.connect(self._update_numobj)
        self.prob_threshold_dial.valueChanged.connect(self._update_prob)
        self.iou_threshold_dial.valueChanged.connect(self._update_iou)
        QtCore.QMetaObject.connectSlotsByName(self.Dialog)

        self.update_curslice()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.Dialog.setWindowTitle(_translate("Dialog", "Non-maximum suppression"))
        self.label_8.setText(_translate("Dialog", "maximum number of objects"))
        self.label_9.setText(_translate("Dialog", "minimum object probability"))
        self.label_10.setText(_translate("Dialog", "minimum intersection/union"))

    def _update_numobj(self) -> bool:
        self.label_numobj.setText(str(self.max_num_objects_dial.value()))
        self.update_curslice()
        self.Dialog.raise_()
        self.Dialog.activateWindow()

        return True

    def _update_prob(self) -> bool:
        self.label_prob.setText(str(self.prob_threshold_dial.value()/100.))
        self.update_curslice()
        self.Dialog.raise_()
        self.Dialog.activateWindow()
        return True

    def _update_iou(self) -> bool:
        self.label_iou.setText(str(self.iou_threshold_dial.value()/100.))
        self.update_curslice()
        self.Dialog.raise_()
        self.Dialog.activateWindow()
        return True

    def parameters(self) -> dict:
        NonMaxDialog.max_num_objects = self.max_num_objects_dial.value()
        NonMaxDialog.prob_threshold = self.prob_threshold_dial.value()/100.
        NonMaxDialog.iou_threshold = self.iou_threshold_dial.value()/100.

        theparameters = {'max_num_objects': NonMaxDialog.max_num_objects,
                         'prob_threshold': NonMaxDialog.prob_threshold,
                         'iou_threshold': NonMaxDialog.iou_threshold}

        return theparameters

    def update_curslice(self) -> bool:
        curslice = self.pjs.curslice

        if self.pjs.batch_classifier.box_arrays[curslice] == []:
            return False

        parameters = self.parameters()
        self.pjs.batch_classifier.non_max_suppression(
            parameters.get('prob_threshold', rimclassifier.DEFAULT_PROB_THRESHOLD),
            parameters.get('iou_threshold', rimclassifier.DEFAULT_IOU_THRESHOLD),
            parameters.get('max_num_objects', rimclassifier.DEFAULT_MAX_NUM_OBJECTS),
            self.pjs.curslice
        )

        self.pjs._cbDeleteCurrentAnn.cbDeleteCurrentAnn()
        self.pjs._cbApplyClassifier.add_classifier_boxes(self.pjs.batch_classifier.box_arrays[curslice][
                                                             self.pjs.batch_classifier.good_box_indices[
                                                                 curslice]], curslice)

        return True

