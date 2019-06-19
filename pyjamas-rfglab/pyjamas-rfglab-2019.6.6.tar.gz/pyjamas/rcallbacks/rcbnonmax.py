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

import numpy
from PyQt5 import QtWidgets

import pyjamas.dialogs as dialogs
from .rcallback import RCallback
from pyjamas.rimage.rimclassifier.rimclassifier import rimclassifier


class RCBNonMax(RCallback):
    def cbNonMaxSuppression(self, parameters: dict = None, first_tp: int = None, last_tp: int = None) -> bool:  # Handle IO errors.
        continue_flag = True

        if parameters is None or parameters is False:
            dialog = QtWidgets.QDialog()
            ui = dialogs.nonmax_suppr.NonMaxDialog(self.pjs)
            ui.setupUi(dialog)
            dialog.exec_()
            dialog.show()

            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted

            if continue_flag:
                parameters = ui.parameters()

            dialog.close()

        if continue_flag:
            if (first_tp is None or first_tp is False) and (last_tp is None or last_tp is False):
                dialog = QtWidgets.QDialog()
                ui = dialogs.timepoints.TimePointsDialog()
                ui.setupUi(dialog, dialogs.timepoints.TimePointsDialog.firstSlice,
                           dialogs.timepoints.TimePointsDialog.lastSlice)

                dialog.exec_()
                dialog.show()

                continue_flag = dialog.result() == QtWidgets.QDialog.Accepted

                if continue_flag:
                    first_tp, last_tp = ui.parameters()

                dialog.close()

            if first_tp <= last_tp:
                theslicenumbers = numpy.arange(first_tp - 1, last_tp, dtype=int)
            else:
                theslicenumbers = numpy.arange(last_tp - 1, first_tp, dtype=int)

            self.pjs.batch_classifier.non_max_suppression(
                parameters.get('prob_threshold', rimclassifier.DEFAULT_PROB_THRESHOLD),
                parameters.get('iou_threshold', rimclassifier.DEFAULT_IOU_THRESHOLD),
                parameters.get('max_num_objects', rimclassifier.DEFAULT_MAX_NUM_OBJECTS),
                theslicenumbers
            )

            for index in theslicenumbers:
                self.pjs._cbDeleteCurrentAnn.cbDeleteCurrentAnn(index)
                self.pjs._cbApplyClassifier.add_classifier_boxes(self.pjs.batch_classifier.box_arrays[index][self.pjs.batch_classifier.good_box_indices[index]], index)

            self.pjs.repaint()

            return True

        else:
            return False

