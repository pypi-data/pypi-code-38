from __future__ import division

import cv2
import numpy as np

from CrystalMatch.dls_imagematch.crystal.align.overlay import Overlayer


class OverlapMetric:

    def __init__(self, image1, image2, metric_upper_limit):
        self.image1 = image1
        self.image2 = image2
        self._metric_upper_limit = metric_upper_limit

    def calculate_overlap_metric(self, offset):
        """ For two images, A and B, where B is offset relative to A, calculate the average
        per pixel absolute difference of the region of overlap of the two images.

        Return the value of this metric as well as an image showing the per pixel absolute
        differences. In the returned image, darker areas indicate greater differences in the
        overlap whereas lighter areas indicate more similarity.
        """
        cr1, cr2 = Overlayer.get_overlap_regions(self.image1, self.image2, offset)

        absdiff_image = cv2.absdiff(cr1.raw(), cr2.raw())
        if absdiff_image is None:
            # The match has failed - return a value above the upper limit for the metric
            return self._metric_upper_limit + 10
        metric = np.sum(absdiff_image) / absdiff_image.size

        return metric
