# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  Copyright (C) 2018
#   Laboratory of Systems Biology, Department of Cybernetics,
#   School of Science, Tallinn University of Technology
#  Authors: Martin Laasmaa and Marko Vendelin
#  This file is part of project: IOCBIO Sparks
#
import numpy as np
from scipy import ndimage

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
import iocbio.sparks.worker as worker


def get_sparks(blurred, std, accept_as_possible_peak, accept_as_possible_area, min_area,
               detector_median_time_px, detector_median_space_px,
               mean=0,
               get_rois=False,
               largest_only=False):
    detector_median_time_px = int(round(detector_median_time_px))
    detector_median_space_px = int(round(detector_median_space_px))
    # mask = ndimage.median_filter( np.where(blurred > mean + accept_as_possible_area*std, 1, 0),
    #                               size=(detector_median_time_px, detector_median_space_px) )
    mask = np.where(blurred > mean + accept_as_possible_area*std, 1, 0)
    label, numlabels = ndimage.label(mask)
    # print('GetSparks: labels found:', numlabels)
    mask_max = ndimage.median_filter( np.where(blurred > mean + accept_as_possible_peak*std, 1, 0),
                                      size=(detector_median_time_px, detector_median_space_px) )
    maxima = ndimage.measurements.maximum(mask_max, label, range(numlabels+1))
    mask_by_criterion = (maxima < 0.5)
    label[ mask_by_criterion[label] ] = 0
    wsizes = ndimage.sum(label.astype(bool), label, range(numlabels+1))
    if largest_only:
        min_area = max(min_area, wsizes.max()*(1-1e-6))
    mask_by_size = (wsizes < min_area)
    label[ mask_by_size[label] ] = 0

    if not get_rois:
        return label

    objects = ndimage.find_objects(label)
    rois = []
    for i in objects:
        if i is not None:
            rois.append([i[0].start, i[1].start, i[0].stop, i[1].stop])
    return label, rois


class AutoDetectSignals(QObject):
    sigRegion = pyqtSignal(list)


class AutoDetect(worker.Job):

    def __init__(self, image, std, accept_as_possible_peak, accept_as_possible_area, min_area, detector_median_time_px, detector_median_space_px):
        worker.Job.__init__(self)
        self.signals = AutoDetectSignals()

        self.image = image
        self.std = std
        self.accept_as_possible_peak = accept_as_possible_peak
        self.accept_as_possible_area = accept_as_possible_area
        self.min_area = min_area
        self.detector_median_time_px = detector_median_time_px
        self.detector_median_space_px = detector_median_space_px

    def run_job(self):
        filtered, regions = get_sparks(self.image, self.std,
                              accept_as_possible_area=self.accept_as_possible_area,
                              accept_as_possible_peak=self.accept_as_possible_peak,
                              min_area=self.min_area,
                              detector_median_time_px=self.detector_median_time_px,
                              detector_median_space_px=self.detector_median_space_px,
                              get_rois=True)

        if self.expired(): return
        for r in regions:
            self.signals.sigRegion.emit(r)
