#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Tue 17 May 15:43:22 CEST 2016

import numpy

from bob.pad.voice.extractor import Ratios
import math

import logging

logger = logging.getLogger("bob.pad.voice")


class VectorsRatios(Ratios):
    def __init__(self,
                 features_processor,  # another extractor that provides features for LBP computation
                 n_bands=5,
                 feature_vector_length=50,
                 vectors_overlap=5,
                 **kwargs
                 ):
        Ratios.__init__(self,
                        features_processor=features_processor,
                        n_bands=n_bands,
                        **kwargs)
        self.feature_vector_length = feature_vector_length
        self.vectors_overlap = vectors_overlap

    def compute_ratios(self, data):
        if len(data) < self.feature_vector_length:
            logger.error(
                "- Extraction: the size of features %d is not enough to construct feature vector of this size: %d",
                len(data), self.feature_vector_length)
            return numpy.zeros(2)

        # carefuly compute the end until we loop
        endloop = len(data) - self.feature_vector_length
        # find the size of each band (a stip of features, for which we compute ratio)
        band_length = math.floor(self.features_processor.n_filters / self.n_bands)
        vector_ratios = []
        # we slide the window through the features shifting by the value of vectors_overlap
        for i in range(0, endloop, self.vectors_overlap):
            # compute ratio between the highest and the lowest band
            lower_band = data[i:i + self.feature_vector_length, 0:band_length]
            higher_band = data[i:i + self.feature_vector_length, -band_length:]
            ratios = [numpy.mean(lower_band) / numpy.mean(higher_band)]

            # compute ratio between the rest of the bands
            for j in range(1, self.n_bands):
                higher_band = data[i:i + self.feature_vector_length, j * band_length:(j + 1) * band_length]
                ratios.append(numpy.mean(lower_band) / numpy.mean(higher_band))
                lower_band = higher_band

            vector_ratios.append(ratios)

        vector_ratios = numpy.asarray(vector_ratios, dtype=numpy.float64)
        return vector_ratios


def __call__(self, input_data, annotations):
    """Use VAD to filter out useless energy bands"""

    if self.features_processor is not None:
        feature_bands = self.features_processor(input_data, annotations)
        if feature_bands.any():
            ratios = self.compute_ratios(feature_bands)
            logger.info("- Extractions: computed ratios of size: %s ", str(ratios.shape))
            return ratios


from .spectrogram_extended import SpectrogramExtended

extractor = VectorsRatios(features_processor=SpectrogramExtended())
