# Copyright (c) 2019 Fabien Georget <fabien.georget@epfl.ch>, EPFL
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from ..core.experiment import PartOfExperiment
from ..utils.coordinates import get_center_areas

import numpy as np
from abc import ABC, abstractmethod
from skimage.segmentation import slic, watershed
from skimage.color import rgb2gray
from skimage.filters import sobel

class SegmentedLabels(PartOfExperiment):
    """The labels issued from segmentation."""
    def __init__(self, labels, composite_parent):
        super().__init__(composite_parent.parent)
        self._labels = labels
        self._init_composite = composite_parent

        self._nb_labels = labels.max()

    @property
    def nb_labels(self):
        """Return the number of labels."""
        return self._nb_labels

    @property
    def labels(self):
        return self._labels

    def get_center_labels(self):
        """Return the centroids of each segmented part."""
        return get_center_areas(self.labels)

    def get_color_labels(self, sampler_points=None, color_img=None):
        """Return the color for the labels."""
        if sampler_points is None:
            sampler_points = self.get_center_labels()
        if color_img is None:
            color_img=self._init_composite.map
        colors = np.zeros((self.nb_labels, 3))
        for i in range(self.nb_labels):
            colors[i,:] = color_img[sampler_points[i,0], sampler_points[i,1], :]
        return colors


class Segmenter(ABC):
   """Abstract base class for a segmenter"""
   def apply(self, composite):
       labels = self.apply_impl(composite)
       return SegmentedLabels(labels, composite)

   @abstractmethod
   def apply_impl():
       """Return the raw labels"""
       #Implement this in segmented subclass
       pass

class SlicSegmenter(Segmenter):
    """The slic segmenter"""
    def __init__(self, compactness, nb_segments, **kwargs):
        self.compactness = compactness
        self.nb_segments = nb_segments
        self.other_args = kwargs

    def apply_impl(self, composite):
        return slic(composite.map,
                    n_segments=self.nb_segments,
                    compactness=self.compactness,
                    **(self.other_args))

class WatershedSegmenter(Segmenter):
    """The watershed segmenter"""
    def __init__(self, markers, **kwargs):
        self.markers = markers
        self.other_args = kwargs

    def apply_impl(self, composite):
        gradient = sobel(rgb2gray(composite.map))
        return watershed(gradient, self.markers, **(self.other_args))