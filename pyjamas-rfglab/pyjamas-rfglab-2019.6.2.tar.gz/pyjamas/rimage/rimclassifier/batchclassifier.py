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

from pyjamas.pjsthreads import ThreadSignals
from pyjamas.rimage.rimclassifier import rimclassifier


class BatchClassifier(object):
    def __init__(self, n_frames: int, classifier: rimclassifier = None):
        self.n_frames = n_frames

        self.prob_arrays = [numpy.empty((1, 0)) for i in range(self.n_frames)]
        self.box_arrays = [numpy.empty((1, 0)) for i in range(self.n_frames)]
        self.good_box_indices = [None for i in range(self.n_frames)]

        if classifier is not None:
            self.image_classifier: rimclassifier = classifier
        else:
            self.image_classifier: rimclassifier = None

    def fit(self) -> bool:
        if self.image_classifier is None:
            return False

        self.image_classifier.fit()

        return True

    def predict(self, slices: numpy.ndarray, indices: numpy.ndarray, progress_signal: ThreadSignals = None) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        indices = numpy.atleast_1d(indices)
        num_slices = len(indices)

        # For every slice ...
        for i, index in enumerate(indices):
            if slices.ndim > 2:
                theimage = slices[index].copy()
            elif slices.ndim == 2 and index == 0:
                theimage = slices.copy()

            self.box_arrays[index], self.prob_arrays[index] = self.image_classifier.predict(theimage)

            if progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def non_max_suppression(self, prob_threshold: float, iou_threshold: float, max_num_objects: int, indices: numpy.ndarray) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        indices = numpy.atleast_1d(indices)

        # For every slice ...
        for index in indices:
            self.good_box_indices[index] = self.image_classifier.non_max_suppression(
                self.box_arrays[index],
                self.prob_arrays[index],
                prob_threshold,
                iou_threshold,
                max_num_objects
            )

        return True

    def load_batch_classifier(self):
        pass

    def save_batch_classifier(self):
        pass

