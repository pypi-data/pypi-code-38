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

from matplotlib.figure import Figure
import numpy
from PyQt5 import QtCore, QtWidgets
import skimage.filters
from skimage.morphology import dilation, square

from .expandseeds import ExpandSeedsDialog
from .matplotlibdialog import MatplotlibDialog
from .propagateseeds import PropagateSeedsDialog
from pyjamas.pjscore import PyJAMAS
from pyjamas.rimage.rimutils import rimutils


class FindSeedsDialog(ExpandSeedsDialog, PropagateSeedsDialog):
    MIN_BINARY_DILATION: int = -10
    MAX_BINARY_DILATION: int = 10
    MIN_SIGMA: float = 0.0
    MAX_SIGMA: float = 10.0
    STEP_SIGMA: float = 0.1
    MIN_DT: float = 0.0
    MAX_DT: float = 50.0
    STEP_DT: float = 0.1

    binary_dilation_number: int = 0
    min_distance_transform: float = -1.0

    preview: bool = True

    def __init__(self, pjs: PyJAMAS):
        super().__init__()

        self.pjs = pjs
        self.image: numpy.ndarray = self.pjs.slices[self.pjs.curslice]
        self.preview_window: MatplotlibDialog = None

    def setupUi(self, Dialog, firstslice=None, lastslice=None, gaussian_sigma=None, winsz=None, bindilation=None,
                mindist=None, preview_flag=None):
        import pyjamas.rcallbacks as rcallbacks

        # Parameter error control.
        if FindSeedsDialog.firstSlice < 0 and firstslice:
            FindSeedsDialog.firstSlice = firstslice
        elif FindSeedsDialog.firstSlice < 0:
            FindSeedsDialog.firstSlice = 0

        if FindSeedsDialog.lastSlice < 0 and lastslice:
            FindSeedsDialog.lastSlice = lastslice
        elif FindSeedsDialog.lastSlice < 0:
            FindSeedsDialog.lastSlice = 1

        if FindSeedsDialog.gaussianSigma < 0:
            FindSeedsDialog.gaussianSigma = rcallbacks.rcbsegment.RCBSegment.DEFAULT_SMOOTHING_SIGMA
        else:
            FindSeedsDialog.gaussianSigma = gaussian_sigma

        if FindSeedsDialog.window_size < 0:
            FindSeedsDialog.window_size = rcallbacks.rcbsegment.RCBSegment.DEFAULT_WINDOW_SZ
        else:
            FindSeedsDialog.window_size = winsz

        if FindSeedsDialog.binary_dilation_number == 0:
            FindSeedsDialog.binary_dilation_number = rcallbacks.rcbsegment.RCBSegment.DEFAULT_BINARY_DILATIONS
        else:
            FindSeedsDialog.binary_dilation_number = bindilation

        if FindSeedsDialog.min_distance_transform < 0:
            FindSeedsDialog.min_distance_transform = rcallbacks.rcbsegment.RCBSegment.DEFAULT_MINIMUM_DISTANCE_TRANSFORM
        else:
            FindSeedsDialog.min_distance_transform = mindist

        if FindSeedsDialog.preview is None:
            FindSeedsDialog.preview = rcallbacks.rcbsegment.RCBSegment.DEFAULT_PREVIEW
        else:
            FindSeedsDialog.preview = preview_flag

        self.dialog = Dialog
        self.dialog.setObjectName("Dialog")
        self.dialog.resize(586, 354)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dialog.sizePolicy().hasHeightForWidth())
        self.dialog.setSizePolicy(sizePolicy)
        self.previewCB = QtWidgets.QCheckBox(self.dialog)
        self.previewCB.setGeometry(QtCore.QRect(30, 277, 87, 20))
        self.previewCB.setObjectName("previewCB")
        self.previewCB.setChecked(FindSeedsDialog.preview)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-150, 307, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox_2 = QtWidgets.QGroupBox(self.dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 20, 181, 101))
        self.groupBox_2.setObjectName("groupBox_2")
        self.sbLast = QtWidgets.QSpinBox(self.groupBox_2)
        self.sbLast.setGeometry(QtCore.QRect(99, 70, 48, 24))
        self.sbLast.setMinimum(1)
        self.sbLast.setMaximum(lastslice)
        self.sbLast.setValue(firstslice)
        self.sbLast.setObjectName("sbLast")
        self.sbFirst = QtWidgets.QSpinBox(self.groupBox_2)
        self.sbFirst.setGeometry(QtCore.QRect(99, 26, 48, 24))
        self.sbFirst.setMinimum(1)
        self.sbFirst.setMaximum(lastslice)
        self.sbFirst.setValue(firstslice)
        self.sbFirst.setObjectName("sbFirst")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(38, 70, 53, 24))
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(35, 26, 56, 24))
        self.label.setObjectName("label")
        self.groupBox_3 = QtWidgets.QGroupBox(self.dialog)
        self.groupBox_3.setGeometry(QtCore.QRect(20, 130, 181, 141))
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        self.label_3.setGeometry(QtCore.QRect(40, 25, 81, 24))
        self.label_3.setObjectName("label_3")
        self.sbGaussianSigma = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.sbGaussianSigma.setGeometry(QtCore.QRect(127, 27, 48, 21))
        self.sbGaussianSigma.setObjectName("sbGaussianSigma")
        self.sbGaussianSigma.setMinimum(FindSeedsDialog.MIN_SIGMA)
        self.sbGaussianSigma.setMaximum(FindSeedsDialog.MAX_SIGMA)
        self.sbGaussianSigma.setValue(FindSeedsDialog.gaussianSigma)
        self.sbGaussianSigma.setSingleStep(FindSeedsDialog.STEP_SIGMA)
        self.sbwinsize = QtWidgets.QSpinBox(self.groupBox_3)
        self.sbwinsize.setGeometry(QtCore.QRect(126, 50, 48, 24))
        self.sbwinsize.setObjectName("sbwinsize")
        self.sbwinsize.setMinimum(FindSeedsDialog.SMALLEST_WINDOW_SIZE)
        self.sbwinsize.setMaximum(FindSeedsDialog.MAX_WINDOW_SIZE)
        self.sbwinsize.setValue(FindSeedsDialog.window_size)
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setGeometry(QtCore.QRect(11, 50, 111, 24))
        self.label_4.setObjectName("label_4")
        self.sbdilation = QtWidgets.QSpinBox(self.groupBox_3)
        self.sbdilation.setGeometry(QtCore.QRect(126, 77, 48, 24))
        self.sbdilation.setObjectName("sbdilation")
        self.sbdilation.setMinimum(FindSeedsDialog.MIN_BINARY_DILATION)
        self.sbdilation.setMaximum(FindSeedsDialog.MAX_BINARY_DILATION)
        self.sbdilation.setValue(FindSeedsDialog.binary_dilation_number)
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setGeometry(QtCore.QRect(25, 77, 111, 24))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.groupBox_3)
        self.label_6.setGeometry(QtCore.QRect(7, 90, 111, 61))
        self.label_6.setObjectName("label_6")
        self.sbMinDT = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.sbMinDT.setGeometry(QtCore.QRect(127, 111, 48, 21))
        self.sbMinDT.setObjectName("sbMinDT")
        self.sbMinDT.setMinimum(FindSeedsDialog.MIN_DT)
        self.sbMinDT.setMaximum(FindSeedsDialog.MAX_DT)
        self.sbMinDT.setValue(FindSeedsDialog.min_distance_transform)
        self.sbMinDT.setSingleStep(FindSeedsDialog.STEP_DT)
        self.preview_window = MatplotlibDialog(self.dialog, self.generate_figure(), "Preview")
        self.preview_window.setGeometry(QtCore.QRect(210, 10, 361, 331))
        self.preview_window.setObjectName("preview_window")

        self.retranslateUi()
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)
        self.previewCB.stateChanged.connect(self.preview_state_changed)
        self.sbGaussianSigma.valueChanged.connect(self.update_preview_window)
        self.sbdilation.valueChanged.connect(self.update_preview_window)
        self.sbwinsize.valueChanged.connect(self.update_preview_window)
        self.sbMinDT.valueChanged.connect(self.update_preview_window)
        QtCore.QMetaObject.connectSlotsByName(self.dialog)

    def accept(self):
        self.close_preview_window()
        self.dialog.accept()

    def reject(self):
        self.close_preview_window()
        self.dialog.reject()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.dialog.setWindowTitle(_translate("Dialog", "Find seeds"))
        self.groupBox_2.setTitle(_translate("Dialog", "Slices"))
        self.label_2.setText(_translate("Dialog", "last slice"))
        self.label.setText(_translate("Dialog", "first slice"))
        self.groupBox_3.setTitle(_translate("Dialog", "Parameters"))
        self.label_3.setText(_translate("Dialog", "smoothing σ"))
        self.label_4.setText(_translate("Dialog", "local window size"))
        self.label_5.setText(_translate("Dialog", "binary dilations"))
        self.label_6.setText(_translate("Dialog", "minimum distance\n"
                                                  "to background"))
        self.previewCB.setText(_translate("Dialog", "preview"))

    def parameters(self):
        FindSeedsDialog.firstSlice = self.sbFirst.value()
        FindSeedsDialog.lastSlice = self.sbLast.value()
        FindSeedsDialog.gaussianSigma = self.sbGaussianSigma.value()
        FindSeedsDialog.window_size = self.sbwinsize.value()
        FindSeedsDialog.binary_dilation_number = self.sbdilation.value()
        FindSeedsDialog.min_distance_transform = self.sbMinDT.value()
        FindSeedsDialog.preview = self.previewCB.isChecked()

        theparameters = {'first': FindSeedsDialog.firstSlice, 'last': FindSeedsDialog.lastSlice,
                         'sigma': FindSeedsDialog.gaussianSigma,
                         'window_size': FindSeedsDialog.window_size,
                         'binary_dilation_number': FindSeedsDialog.binary_dilation_number,
                         'min_distance_transform': FindSeedsDialog.min_distance_transform,
                         'preview': FindSeedsDialog.preview}

        return theparameters

    def preview_state_changed(self) -> bool:
        self.preview = self.previewCB.isChecked()

        if self.preview:
            # create display figure and display intermediate steps.
            self.update_preview_window()

        return True

    def close_preview_window(self) -> bool:
        self.preview_window.close()
        self.preview_window = None

        return True

    def update_preview_window(self) -> bool:
        if self.preview:
            self.preview_window.set_figure(self.generate_figure())

        return True

    def generate_figure(self) -> Figure:
        import pyjamas.rcallbacks as rcallbacks

        parameters = self.parameters()
        theimage = skimage.filters.gaussian(self.image, parameters['sigma'], multichannel=False)
        _, intermediate_images = rimutils.find_seeds(theimage, parameters.get('window_size',
                                                                              rcallbacks.rcbsegment.RCBSegment.DEFAULT_WINDOW_SZ),
                                                     parameters.get('binary_dilation_number',
                                                                    rcallbacks.rcbsegment.RCBSegment.DEFAULT_BINARY_DILATIONS),
                                                     parameters.get('min_distance_transform',
                                                                    rcallbacks.rcbsegment.RCBSegment.DEFAULT_MINIMUM_DISTANCE_TRANSFORM))
        figure, ax = rimutils.figdisplay(
            ((theimage, intermediate_images[0].astype(int)), (intermediate_images[1], self.image)),
            image_titles=(('smooth', 'threshold'), ('distance', 'seeds')), display=False)
        ax[1, 1].imshow(dilation(intermediate_images[2], square(10)), cmap='jet', alpha=.5)

        return figure
