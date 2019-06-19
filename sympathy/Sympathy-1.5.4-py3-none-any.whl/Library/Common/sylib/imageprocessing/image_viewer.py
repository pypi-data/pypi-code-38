# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import PySide.QtGui as QtGui
from PySide.QtCore import Qt
import numpy as np

from sympathy.api.typeutil import ViewerBase
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas)
from matplotlib.backends.backend_qt4agg import (
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


def handle_complex(method, data):
    if method == ImageCanvas.COMPLEX_REAL:
        return np.real(data)
    elif method == ImageCanvas.COMPLEX_IMAGINARY:
        return np.imag(data)
    elif method == ImageCanvas.COMPLEX_MAGNITUDE:
        return np.abs(data)
    elif method == ImageCanvas.COMPLEX_PHASE:
        return np.angle(data)
    raise ValueError("Invalid method in handle_complex")


class ImageCanvas(FigureCanvas):

    RANGE_DEFAULT   = 0
    RANGE_CLAMP     = 1
    RANGE_NORMALIZE = 2
    COMPLEX_REAL      = 0
    COMPLEX_IMAGINARY = 1
    COMPLEX_MAGNITUDE = 2
    COMPLEX_PHASE     = 3

    def __init__(self, parent=None):
        plt.style.use('grayscale')
        fig = Figure(figsize=(8, 5), dpi=75)
        fig.patch.set_facecolor('none')
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(
            self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def update_image(self, image, channel, range_method,
                     complex_method, complex_widget, aspect='equal'):
        self.axes.clear()
        if image is None:
            return

        full_color = False
        if len(image.shape) < 3:
            selected_channels = image
        elif image.shape[2] == 1:
            selected_channels = image.reshape(image.shape[:2])
        else:
            if (channel == image.shape[2] and
                (image.shape[2] == 3 or image.shape[2] == 4)):
                full_color = True
                selected_channels = image[:, :, :3]
            else:
                selected_channels = (
                    image[:, :, channel].reshape(image.shape[:2]))

        if range_method == self.RANGE_CLAMP:
            kwargs = dict(vmin=0.0, vmax=1.0)
            selected_channels = np.maximum(
                0.0, np.minimum(1.0, selected_channels))
        elif range_method == self.RANGE_NORMALIZE:
            minimum = np.min(selected_channels)
            maximum = np.max(selected_channels)
            selected_channels = selected_channels / (maximum-minimum) - minimum
            kwargs = dict()
        else:
            kwargs = dict(vmin=0.0, vmax=1.0)

        if not full_color:
            if (np.issubdtype(selected_channels.dtype, np.integer) and
                np.max(selected_channels) > 1):
                kwargs = dict(cmap='Paired', interpolation='nearest')
            elif np.issubdtype(selected_channels.dtype, np.integer):
                kwargs = dict(cmap='gray', interpolation='nearest')
            elif selected_channels.dtype is np.bool:
                kwargs = dict(cmap='gray', interpolation='nearest')
            else:
                kwargs = dict(cmap='gray', **kwargs)

        if selected_channels.dtype == np.complexfloating:
            complex_widget.setVisible(True)
            selected_channels = handle_complex(complex_method,
                                               selected_channels)
        else:
            complex_widget.setVisible(False)

        # Later versions of matplot lib require floatingpoint RGB images
        # to be in range 0.0 - 1.0
        if full_color and selected_channels.dtype == np.float:
            selected_channels = np.maximum(0.0, np.minimum(1.0, selected_channels))

        kwargs['aspect'] = aspect
        self.axes.imshow(selected_channels, **kwargs)
        self.draw()


class HistogramCanvas(FigureCanvas):

    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 2.5), dpi=75)
        fig.patch.set_facecolor('none')
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(
            self, QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        FigureCanvas.updateGeometry(self)

    def update_image(self, image, channel, logscale, complex_method):
        self.axes.clear()
        # self.axes.set_xticks([])
        # self.axes.set_yticks([])
        # self.axes.set_axis_bgcolor('white')
        if image is None:
            return

        full_color = False
        if len(image.shape) < 3:
            selected_channels = image
        elif image.shape[2] == 1:
            selected_channels = image.reshape(image.shape[:2])
        else:
            if (channel == image.shape[2] and
                (image.shape[2] == 3 or image.shape[2] == 4)):
                full_color = True
                selected_channels = image
            else:
                selected_channels = (
                    image[:, :, channel].reshape(image.shape[:2]))

        if selected_channels.dtype == np.complex:
            selected_channels = handle_complex(complex_method,
                                               selected_channels)

        try:
            if full_color:
                self.axes.hist(
                    [selected_channels[:, :, ch].ravel()
                     for ch in range(3)],
                    bins=256, histtype='step',
                    color=['red', 'green', 'blue'], log=logscale)
            else:
                self.axes.hist(selected_channels.ravel()*1, bins=256, log=logscale)
        except ValueError:
            pass

        self.draw()


class ImageViewer(ViewerBase):
    def __init__(self, data=None, console=None, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image_canvas     = ImageCanvas()
        self.histogram_canvas = HistogramCanvas()
        self.enable_updates   = False

        # Main layout consisting of toolbar and content-layout
        self.main_layout = QtGui.QVBoxLayout()
        self.toolbar     = NavigationToolbar(self.image_canvas, self)
        self.main_layout.addWidget(self.toolbar)

        # Content layout, consisting of image canvas and options-layout
        self.content_layout = QtGui.QHBoxLayout()
        self.horz_splitter = QtGui.QSplitter()
        self.horz_splitter.setOrientation(Qt.Horizontal)
        self.horz_splitter.setLayout(self.content_layout)

        # self.main_layout.addLayout(self.content_layout)
        self.main_layout.addWidget(self.horz_splitter)

        self.optionsWidget = QtGui.QGroupBox('Options')
        self.optionsLayout = QtGui.QVBoxLayout()
        self.optionsWidget.setLayout(self.optionsLayout)

        self.content_layout.addWidget(self.image_canvas)
        self.content_layout.addWidget(self.optionsWidget)

        # Combo-box for selecting channel to view
        self.channel_select = QtGui.QComboBox()
        self.channel_select.setCurrentIndex(-1)
        self.channel_select.currentIndexChanged.connect(self.channel_selected)
        self.add_option('Channel: ', self.channel_select)

        # Combo-box for selecting color range handling method
        self.color_range_select = QtGui.QComboBox()
        self.color_range_select.addItem("Default")
        self.color_range_select.addItem("Clamp")
        self.color_range_select.addItem("Normalize")
        self.add_option('Color range:', self.color_range_select)
        self.color_range_select.currentIndexChanged.connect(
            self.color_range_selected)
        self.color_range = 0

        # Combo-box for selecting method to view complex numbers
        self.complex_select = QtGui.QComboBox()
        self.complex_select.addItem("Real")
        self.complex_select.addItem("Imaginary")
        self.complex_select.addItem("Magnitude")
        self.complex_select.addItem("Phase")
        self.opt_complex = self.add_option('Complex numbers:',
                                           self.complex_select)
        self.complex_select.currentIndexChanged.connect(
            self.complex_selected)
        self.complex = 0

        self.aspect_select = QtGui.QComboBox()
        self.aspect_select.addItem("1:1")
        self.aspect_select.addItem("Fill")
        self.aspect_options = ['equal', 'auto']
        self.aspect = self.aspect_options[0]
        self.opt_aspect = self.add_option('Aspect ratio:', self.aspect_select)
        self.aspect_select.currentIndexChanged.connect(
            self.aspect_selected)

        # Information and histogram
        self.optionsLayout.addStretch(1)
        self.dtype_widget = QtGui.QLabel("")
        self.add_option("Datatype: ", self.dtype_widget)
        self.shape_widget = QtGui.QLabel("")
        self.add_option("Shape: ", self.shape_widget)
        self.minmax_widget = QtGui.QLabel("")
        self.add_option("Min/max value: ", self.minmax_widget)

        self.log_button = QtGui.QCheckBox()
        self.add_option('Histogram log-scale', self.log_button)
        self.log_button.stateChanged.connect(
            lambda index, self_=self: self_.update_images())

        # Add histogram at bottom
        self.optionsLayout.addWidget(self.histogram_canvas)

        # Attach everything
        self.setLayout(self.main_layout)

        if data is None:
            self.image = None
        else:
            self.image = data.get_image()
        self.enable_updates = True

    def add_option(self, text, widget):
        hbox_widget = QtGui.QWidget()
        hbox = QtGui.QHBoxLayout()
        hbox_widget.setLayout(hbox)
        hbox.addWidget(QtGui.QLabel(text))
        hbox.addWidget(widget)
        self.optionsLayout.addWidget(hbox_widget)
        return hbox_widget

    def data(self):
        return self._data

    def update_images(self):

        self.image_canvas.update_image(
            self.image, self.selected_channel,
            self.color_range, self.complex,
            self.opt_complex, aspect=self.aspect)
        self.histogram_canvas.update_image(
            self.image, self.selected_channel,
            self.log_button.isChecked(),
            self.complex)

    def update_data(self, data):
        self.enable_updates = False
        self._data = data
        if data is None:
            self.image = None
        else:
            self.image = data.get_image()

        if np.issubdtype(self.image.dtype, np.complexfloating):
            self.minmax_widget.setText(
                "{0:.2}{1:+.2}j / {2:.2}{3:+.2}j"
                .format(np.min(np.real(self.image)),
                        np.min(np.imag(self.image)),
                        np.max(np.real(self.image)),
                        np.max(np.imag(self.image))))
        elif np.issubdtype(self.image.dtype, np.floating):
            self.minmax_widget.setText(
                "{0:.2} / {1:.2}"
                .format(np.min(self.image), np.max(self.image)))
        else:
            self.minmax_widget.setText(
                "{0} / {1}".format(np.min(self.image), np.max(self.image)))
        self.dtype_widget.setText("{0}".format(self.image.dtype))
        self.shape_widget.setText("{0}".format(self.image.shape))

        self.update_channel_selections()
        self.enable_updates = True
        self.update_images()

    def update_channel_selections(self):
        if self.image is None:
            self.num_channels = 1
            return

        if len(self.image.shape) < 3:
            self.num_channels = 1
        else:
            self.num_channels = self.image.shape[2]

        self.channel_select.setCurrentIndex(-1)
        while self.channel_select.count() > 0:
            self.channel_select.removeItem(0)

        for i in range(self.num_channels):
            self.channel_select.addItem('Channel {0}'.format(i))
        if self.num_channels == 3 or self.num_channels == 4:
            self.selected_channel = self.num_channels
            self.channel_select.addItem('Full color')
            self.channel_select.setCurrentIndex(self.num_channels)
        else:
            self.selected_channel = 0
            self.channel_select.setCurrentIndex(0)

    def channel_selected(self, index):
        self.selected_channel = index
        if index >= 0 and self.enable_updates:
            self.update_images()

    def color_range_selected(self, index):
        self.color_range = index
        if self.enable_updates:
            self.update_images()

    def complex_selected(self, index):
        self.complex = index
        if self.enable_updates:
            self.update_images()

    def aspect_selected(self, index):
        self.aspect = self.aspect_options[index]
        if self.enable_updates:
            self.update_images()
