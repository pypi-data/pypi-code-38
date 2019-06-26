# ================================================================================ #
#   Authors: Fabio Frazao and Oliver Kirsebom                                      #
#   Contact: fsfrazao@dal.ca, oliver.kirsebom@dal.ca                               #
#   Organization: MERIDIAN (https://meridian.cs.dal.ca/)                           #
#   Team: Data Analytics                                                           #
#   Project: ketos                                                                 #
#   Project goal: The ketos library provides functionalities for handling          #
#   and processing acoustic data and applying deep neural networks to sound        #
#   detection and classification tasks.                                            #
#                                                                                  #
#   License: GNU GPLv3                                                             #
#                                                                                  #
#       This program is free software: you can redistribute it and/or modify       #
#       it under the terms of the GNU General Public License as published by       #
#       the Free Software Foundation, either version 3 of the License, or          #
#       (at your option) any later version.                                        #
#                                                                                  #
#       This program is distributed in the hope that it will be useful,            #
#       but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#       GNU General Public License for more details.                               # 
#                                                                                  #
#       You should have received a copy of the GNU General Public License          #
#       along with this program.  If not, see <https://www.gnu.org/licenses/>.     #
# ================================================================================ #

""" Annotation module within the ketos library

    This module provides utilities to handle annotations associated 
    with audio files and spectrograms.

    Contents:
        AnnotationHandler class: 
"""

from ketos.utils import ndim
import numpy as np
import math


class AnnotationHandler():
    """ Parent class for the AudioSignal and Spectrogram classes.

        An annotation consists of an integer label (0,1,2,...) and 
        a bounding box that delimits the audio segment of interest 
        in time and optionally frequency. 
        
        The bounding box is a list of four floats: start time, end time,
        minimum frequency, and maximum frequency (with frequency expressed in Hz)
        A list of two floats ([start time, end time]) can also be used in the initialization.
        In this case, the minimum and maximum frequencies will be respectivelly filled as 0 and Inf.
        is interpreted as the start and end time of the 
        segment (in seconds). list of four floats is interpreted as 
        .

        Args:
            labels: list(int)
                List of annotation labels
            boxes: list(tuple)
                List of bounding boxes, each specifying a time interval (in seconds)
                and optionally also a frequency interval (in Hz).
                The format is [t_min, t_max, f_min, f_max]

        Attributes:
            labels: list(int)
                List of annotation labels
            boxes: list(tuple)
                List of bounding boxes, each specifying a time interval (in seconds)
                and optionally also a frequency interval (in Hz).
                The format is [t_min, t_max, f_min, f_max]
            precision: int
                Number of decimals used for bounding box values
    """
    def __init__(self, labels=None, boxes=None):

        self.labels = []
        self.boxes = []
        self.precision = 3

        if labels is not None:
            self.annotate(labels, boxes)

    def annotate(self, labels, boxes):
        """ Add a set of annotations.
            
            Args:
                labels: list(int)
                    Annotation labels.
                boxes: list(tuple)
                    Annotation boxes, specifying the start and stop time of the annotation 
                    and, optionally, the minimum and maximum frequency.

            Example:
                >>> from ketos.audio_processing.annotation import AnnotationHandler
                >>> 
                >>> handler = AnnotationHandler()
                >>> labels = [0, 1]
                >>> boxes = [[10.0, 12.2, 110., 700.],[30., 34.]]
                >>> handler.annotate(labels, boxes)
                >>> print(handler.labels)
                [0, 1]
                >>> print(handler.boxes)
                [[10.0, 12.2, 110.0, 700.0], [30.0, 34.0, 0, inf]]
        """
        if ndim(labels) == 0:
            labels = [labels]

        if ndim(boxes) == 1 and len(boxes) > 0:
            boxes = [boxes]

        assert len(labels) == len(boxes), 'number of labels must equal number of boxes'
        assert ndim(labels) == 1, 'labels list has invalid dimension'
        assert ndim(boxes) == 2 or (ndim(boxes) == 1 and len(boxes) == 0), 'boxes list has invalid dimension'

        for l,b in zip(labels, boxes):
            b = self._ensure4D(b)
            self.labels.append(l)
            self.boxes.append(b)

        for b in self.boxes:
            b = np.array(b).tolist()

    def _ensure4D(self, b):
        """ Ensure that the annotation box has four entries.

            Set the minimum frequency to 0 and the maximum 
            frequency to infinity, if these are missing.
            
            Args:
                b: list or tuple
                   Bounding box with two or four entries 
        """
        for v in b:
            v = round(v, self.precision)

        if len(b) == 2:
            b = [b[0], b[1], 0, math.inf]
        
        assert len(b) == 4, 'Found box with {0} entries; all boxes must have either 2 or 4 entries'.format(len(b))
        
        return b

    def delete_annotations(self, id=None):
        """ Delete the annotation with the specified ID(s).

            If no ID is spefied, all annotations are deleted.
            
            Args:
                id: int or list(int)
                    ID of the annotation to be deleted.

            Example:
                >>> from ketos.audio_processing.annotation import AnnotationHandler
                >>> 
                >>> labels = [0, 1]
                >>> boxes = [[10.0, 12.2, 110., 700.],[30., 34.]]
                >>> handler = AnnotationHandler(labels, boxes)
                >>> handler.delete_annotations(0)
                >>> print(handler.labels)
                [1]
                >>> print(handler.boxes)
                [[30.0, 34.0, 0, inf]]
        """
        if id is None:
            self.labels = []
            self.boxes = []
        else:
            if ndim(id) == 0:
                id = [id]
            # sort id's in ascending order 
            id = sorted(id, reverse=True)
            # loop over id's
            for i in id:
                if i < len(self.labels):
                    # delete specified annotations
                    del self.labels[i]
                    del self.boxes[i]

    def get_cropped_annotations(self, t1=0, t2=math.inf, f1=0, f2=math.inf):
        """ Update boundary boxes in response to cropping operation in time and/or frequency.
            
            Args:
                t1: float
                    Lower time cut in seconds
                t2: float
                    Upper time cut in seconds
                f1: float
                    Lower frequency cut in Hz
                f2: float
                    Upper frequency in in Hz

            Example:
                >>> from ketos.audio_processing.annotation import AnnotationHandler
                >>> 
                >>> labels = [0, 1]
                >>> boxes = [[10.0, 12.2, 110., 700.],[30., 34.]]
                >>> handler = AnnotationHandler(labels, boxes)
                >>> cropped_labels, cropped_boxes = handler.get_cropped_annotations(t1=10.3, f2=555.)
                >>> print(cropped_labels)
                [0, 1]
                >>> print(cropped_boxes)
                [[10.3, 12.2, 110.0, 555.0], [30.0, 34.0, 0, 555.0]]
        """
        if t1 is None: t1 = 0
        if t2 is None: t2 = math.inf
        if f1 is None: f1 = 0
        if f2 is None: f2 = math.inf

        labels, boxes = [], []

        # loop over annotations
        for l, b in zip(self.labels, self.boxes):

            # check if box overlaps with cut
            if b[0] < t2 and b[1] > t1 and b[2] < f2 and b[3] > f1:

                # update box boundaries
                b0 = max(b[0], t1)
                b1 = min(b[1], t2)
                b2 = max(b[2], f1)
                b3 = min(b[3], f2)

                # truncate to desired precision
                b0 = round(b0, self.precision)
                b1 = round(b1, self.precision)
                b2 = round(b2, self.precision)
                b3 = round(b3, self.precision)

                # new bounding box
                box = [b0, b1, b2, b3]

                labels.append(l)
                boxes.append(box)

        return labels, boxes

    def _shift_annotations(self, delay=0):
        """ Shift all annotations by a fixed time interval.
            
            Args:
                delay: float
                    Time shift in seconds.

            Example:
                >>> from ketos.audio_processing.annotation import AnnotationHandler
                >>> 
                >>> labels = 1
                >>> boxes = [10.0, 12.2]
                >>> handler = AnnotationHandler(labels, boxes)
                >>> handler._shift_annotations(2.0)
                >>> print(handler.boxes)
                [[12.0, 14.2, 0, inf]]
        """
        for b in self.boxes:
            b[0] += delay
            b[1] += delay
            for v in b: 
                v = round(v, self.precision)
        
    def _scale_annotations(self, scale=0):
        """ Scale the time axis by a constant factor.
            
            Args:
                scale: float
                    Scaling factor.

            Example:
                >>> from ketos.audio_processing.annotation import AnnotationHandler
                >>> 
                >>> labels = 1
                >>> boxes = [10.0, 12.2]
                >>> handler = AnnotationHandler(labels, boxes)
                >>> handler._scale_annotations(2.0)
                >>> print(handler.boxes)
                [[20.0, 24.4, 0, inf]]
        """
        for b in self.boxes:
            b[0] *= scale
            b[1] *= scale
            for v in b: 
                v = round(v, self.precision)
