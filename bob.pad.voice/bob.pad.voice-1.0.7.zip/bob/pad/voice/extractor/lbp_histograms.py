#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Tue 17 May 15:43:22 CEST 2016

import numpy
import bob.io.base
import bob.ip.base

import bob.sp

from bob.pad.voice.extractor import LBPs

import logging

logger = logging.getLogger("bob.pad.voice")

class LBPHistograms(LBPs):
    """
    Extractor that computes histograms of LBP features from a textogram, which, in turn, is computed by a cepstral
    or spectral extractor passed as an argument.
    """

    def __init__(self,
                 features_processor,  # another extractor that provides features for LBP computation
                 n_lbp_histograms=2,
                 lbp_neighbors=16,
                 lbp_to_average=False,
                 lbp_uniform=False,
                 lbp_radius=1,
                 lbp_circular=True,
                 lbp_elbp_type='regular',
                 histograms_for_rows = False,
                 band_ratios=True,
                 **kwargs
                 ):
        LBPs.__init__(self,
                      features_processor = features_processor,
                      n_lbps=n_lbp_histograms,
                      lbp_neighbors=lbp_neighbors,
                      lbp_to_average=lbp_to_average,
                      lbp_uniform=lbp_uniform,
                      lbp_radius=lbp_radius,
                      lbp_circular=lbp_circular,
                      lbp_elbp_type=lbp_elbp_type,
                      band_ratios=band_ratios,
                      **kwargs)
        self.histograms_for_rows = histograms_for_rows


    def compute_histograms(self, lbp_wrapper, lbpimages):
        histograms = []
        current_hist =[]
        for i in range(0, self.n_bands):
            if self.histograms_for_rows:
                for j in range(0, lbpimages[i].shape[1]):
                    # "histograms are individually normalized"
                    row_hist, _ = numpy.histogram(lbpimages[i][:, j], bins=lbp_wrapper.max_label,
                                                  range=(0, lbp_wrapper.max_label - 1), density=True)
                    current_hist = numpy.append(current_hist,
                                                numpy.asarray(row_hist).flatten())  # just put into the larger list
            else:
                current_hist = bob.ip.base.histogram(lbpimages[i], (0, lbp_wrapper.max_label - 1),
                                                     lbp_wrapper.max_label)
                if sum(current_hist) != 0:
                    current_hist = current_hist / sum(current_hist)  # histogram normalization

                # reduce dimension of the features if lbp is for 16 neighbors
                if self.lbp_neighbors == 16:
                    current_hist_fft = bob.sp.fft(numpy.asarray(current_hist, dtype=numpy.complex128))
                    current_hist = current_hist_fft.real[0:16]  # take only first 16 frequencies of the real part



            histograms.append(current_hist)  # just put into the larger list
        return histograms

    def __call__(self, input_data, annotations=None):
        """Computed LBP histograms from cepstral or spectrogram features"""

        # spectrogram = SpectrogramExtended.__call__(input_data, annotations)
        spectrogram = self.get_features(input_data, annotations)

        lbpwrapper, lbpimages = self.compute_lbps(spectrogram)
        lbp_histograms = self.compute_histograms(lbpwrapper, lbpimages)
        ratios = []
        if self.band_ratios:
            ratios = self.compute_ratios(spectrogram)

        # concatenate histograms together in one numpy array
        features = numpy.append(ratios, lbp_histograms)
        logger.info("- Extraction: size of the LBP histogram feature vector of size %s", str(features.shape))

        return numpy.asarray(features, dtype=numpy.float64)


from .spectrogram_extended import SpectrogramExtended
extractor = LBPHistograms(features_processor=SpectrogramExtended())
