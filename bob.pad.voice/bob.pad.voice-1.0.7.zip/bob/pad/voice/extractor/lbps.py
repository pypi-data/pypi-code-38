#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Tue 17 May 15:43:22 CEST 2016

import numpy
import bob.io.base
import bob.ip.base

import bob.sp

from .ratios import Ratios

import math

import logging

logger = logging.getLogger("bob.pad.voice")

class LBPs(Ratios):
    """
    Extractor that computes histograms of LBP features from a textogram, which, in turn, is computed by a cepstral
    or spectral extractor passed as an argument.
    """

    def __init__(self,
                 features_processor,  # another extractor that provides features for LBP computation
                 n_lbps=2,
                 lbp_neighbors=16,
                 lbp_to_average=False,
                 lbp_uniform=False,
                 lbp_radius=1,
                 lbp_circular=True,
                 lbp_elbp_type='regular',
                 band_ratios=True,
                 **kwargs
                 ):
        Ratios.__init__(self,
                        features_processor=features_processor,
                        n_bands=n_lbps,
                           **kwargs)
        self.lbp_neighbors = lbp_neighbors
        self.lbp_to_average = lbp_to_average
        self.lbp_elbp_type = lbp_elbp_type
        self.lbp_uniform = lbp_uniform
        self.lbp_circular = lbp_circular
        self.lbp_radius = lbp_radius
        self.band_ratios = band_ratios


    def compute_lbps(self, data):
        # find the size of each textogram (a stip of features, for which we compute LBP)
        textogram_width = int(math.floor(self.features_processor.n_filters / self.n_bands))
        lbpimages = []
        lbp = bob.ip.base.LBP(neighbors=self.lbp_neighbors, circular=self.lbp_circular,
                              radius=self.lbp_radius, to_average=self.lbp_to_average,
                              uniform=self.lbp_uniform, elbp_type=self.lbp_elbp_type)

        for i in range(0, self.n_bands):
            textogram = data[:, i * textogram_width:(i + 1) * textogram_width]
            if textogram.max():
                textogram *= 255.0 / textogram.max()
            textogram = numpy.asarray(textogram, dtype=numpy.uint8)


            lbpimage = numpy.ndarray(lbp.lbp_shape(textogram), 'uint16')  # allocating the image with lbp codes
            lbp(textogram, lbpimage)  # calculating the lbp image
            lbpimages.append(lbpimage)

        return lbp, lbpimages

    def get_features(self, input_data, annotations):
        # spectrogram = SpectrogramExtended.__call__(input_data, annotations)
        if self.features_processor is not None:
            return self.features_processor(input_data, annotations)

        logger.info("- Extraction: spectrogram is empty, returning zero vector...")
        hist_size = 1
        if self.lbp_neighbors == 16:
            hist_size = 16  # we keep only 16 fft coefficients
        elif self.lbp_neighbors == 8:
            hist_size = 256  # the size of histograms when LBP is computed on 8 neighbors
        return numpy.array([numpy.zeros(hist_size * self.n_bands + self.n_bands)])

    def __call__(self, input_data, annotations=None):
        """Computed LBP histograms from cepstral or spectrogram features"""

        # spectrogram = SpectrogramExtended.__call__(input_data, annotations)
        spectrogram = self.get_features(input_data, annotations)

        lbp, lbpimages = self.compute_lbps(spectrogram)
        ratios = []
        if self.band_ratios:
            ratios = self.compute_ratios(spectrogram)

        # concatenate histograms together in one numpy array
        features = []
        for i in range(0, self.n_bands):
            features.append(lbpimages[i].flatten())  # just put into the larger list

        features = numpy.append(ratios, features)
        logger.info("- Extraction: size of the LBP feature vector of size %s", str(features.shape))

        return numpy.asarray(features, dtype=numpy.float64)


from .spectrogram_extended import SpectrogramExtended
extractor = LBPs(features_processor=SpectrogramExtended())
