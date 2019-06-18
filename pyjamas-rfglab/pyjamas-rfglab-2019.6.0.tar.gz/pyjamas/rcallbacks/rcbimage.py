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

import time
from typing import List

import numpy
from PyQt5 import QtCore, QtWidgets

from pyjamas.pjsthreads import Thread
from pyjamas.rcallbacks.rcallback import RCallback
from pyjamas.rimage.rimutils import rimutils
from pyjamas.rutils import RUtils


class RCBImage(RCallback):
    CW: int = 90
    CCW: int = -90
    UP_DOWN: int = 1
    LEFT_RIGHT: int = 2

    def cbRotateImage(self, direction: int = CW) -> bool:
        if direction == self.CW:
            # self.pjs.slices = numpy.asarray([numpy.rot90(x, -1) for x in self.pjs.slices]) # An order of magnitude slower than below.
            self.pjs.slices = numpy.rot90(self.pjs.slices, -1, (1, 2))

        elif direction == self.CCW:
            # self.pjs.slices = numpy.asarray([numpy.rot90(x) for x in self.pjs.slices]) # An order of magnitude slower than below.
            self.pjs.slices = numpy.rot90(self.pjs.slices, 1, (1, 2))

        self.pjs.initImage()

        return True

    def cbFlipImage(self, direction: int = LEFT_RIGHT) -> bool:
        if direction == self.LEFT_RIGHT:
            # self.pjs.slices = numpy.flip(self.pjs.slices, 2)  # Order or magnitude slower than the code below.
            self.pjs.slices = self.pjs.slices[..., ::-1]
        elif direction == self.UP_DOWN:
            # self.pjs.slices = numpy.fliplr(self.pjs.slices)  # Could have used flip with parameter 1, but this is faster. Unfortunately, there is no fast function to flip with parameter 2. Still, slower than below.
            self.pjs.slices = self.pjs.slices[..., ::-1, :]

        self.pjs.initImage()

        return True

    def cbMIPImage(self, slice_list: List[int]) -> bool:
        if slice_list is False:
            slice_list_str, ok_pressed = QtWidgets.QInputDialog.getText(None, "Maximum intenstiy projection", "Enter a range of slices (e.g. 0, 1, 4-8, 15): ", QtWidgets.QLineEdit.Normal, "")

            if not ok_pressed:
                return False

            if slice_list_str == '':
                slice_list = list(range(self.pjs.n_frames))
            else:
                slice_list = RUtils.parse_range_list(slice_list_str)

        # This line here is necessary: for some mysterious reason, if doing an MIP from a slice
        # other than the first one, there is an error that I was unable to debug, but seemed related
        # to the Qt backend based on the debugger error.
        """/Users/rodrigo/src/pyjamas/pyjamas/rimage/rimutils.py:641: RuntimeWarning: divide by zero encountered in true_divide
            sc = (maximum - minimum) / (high - low)
            /Users/rodrigo/src/pyjamas/pyjamas/rimage/rimutils.py:648: RuntimeWarning: invalid value encountered in multiply
            image_out = image_out * sc"""
        self.pjs._cbTimeSlider.cbGoTo(0)

        self.pjs.slices = rimutils.mip(self.pjs.slices[slice_list])

        self.pjs.initImage()

        return True

    def cbInvertImage(self) -> bool:
        self.pjs.slices = rimutils.invert(self.pjs.slices)
        self.pjs.prepare_image()

        self.pjs.displayData()

        return True

    def cbRegisterImage(self) -> bool:
        working_slice = self.pjs.curslice
        self.pjs.slices, distances = rimutils.register(self.pjs.slices, RUtils.pjsfiducials_to_array(self.pjs.fiducials), self.pjs.curslice)
        self.shift_annotations(distances)
        self.pjs.prepare_image()
        self.pjs._cbTimeSlider.cbGoTo(working_slice)

        self.pjs.displayData()

        return True

    # Inspiration for multithreading from: # Shamelessly stolen from https://www.mfitzp.com/article/multithreading-pyqt-applications-with-qthreadpool/
    def cbPlay(self) -> bool: # oh_no
        athread = Thread(self.play_movie)
        athread.kwargs['progress_callback'] = athread.signals.progress
        #athread.signals.result.connect(self.print_output)
        athread.signals.finished.connect(self.thread_complete)
        athread.signals.progress.connect(self.progress_fn)

        self.pjs.threadpool.start(athread)

        return True

    def play_movie(self, progress_callback) -> bool: #execute_this_fn
        start = time.time()
        period = 1.0 / self.pjs.fps

        while self.pjs.curslice < self.pjs.n_frames - 1:
            if (time.time() - start) > period:
                start += period
                # Because this is the function that will run in a thread, it cannot
                # manipulate the gui (or errors will happen - gui manipulations must
                # be in the thread that owns the gui). Instead, we can emit a signal
                # when it corresponds, and the signal can be slotted in a function
                # in the main thread that modifies the gui.
                #self.pjs._cbNextFrame.cbNextFrame()
                progress_callback.emit(self.pjs.curslice)

        return True

    def progress_fn(self, n):
        self.pjs._cbNextFrame.cbNextFrame()

    def thread_complete(self):
        self.pjs._cbTimeSlider.cbGoTo(0)

    def shift_annotations(self, translation_vector: numpy.ndarray) -> bool:
        if translation_vector is False or translation_vector is None:
            return False

        for slice_index in range(self.pjs.n_frames):
            theshift = translation_vector[slice_index].astype(int)

            for fiducial_index, _ in enumerate(self.pjs.fiducials[slice_index]):
                 self.pjs.fiducials[slice_index][fiducial_index] += theshift

            for a_polyline in self.pjs.polylines[slice_index]:
                a_polyline.translate(QtCore.QPointF(theshift[0], theshift[1]))

        return True