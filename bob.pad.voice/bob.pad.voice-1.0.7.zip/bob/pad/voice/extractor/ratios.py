#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Tue 17 May 15:43:22 CEST 2016

import numpy
import bob.io.base

from bob.bio.base.extractor import Extractor
import math

import logging

logger = logging.getLogger("bob.pad.voice")


class Ratios(Extractor):
    def __init__(self,
                 features_processor,  # another extractor that provides features for LBP computation
                 n_bands=5,
                 **kwargs
                 ):
        Extractor.__init__(self,
                           requires_training=False, split_training_data_by_client=False,
                           **kwargs)
        self.n_bands = n_bands

        assert isinstance(features_processor, bob.bio.base.extractor.Extractor), \
            "Only feature processors derived from bob.bio.base.extractor.Extractor are supported in this class. "

        self.features_processor = features_processor


    def compute_ratios(self, data):
        # find the size of each band (a stip of features, for which we compute ratio)
        band_length = int(math.floor(self.features_processor.n_filters / self.n_bands))
        # compute ratio between the highest and the lowest band
        lower_band = data[:, 0:band_length]
        higher_band = data[:, -band_length:]
        ratios = [numpy.mean(higher_band) / numpy.mean(lower_band)]
        # compute ratio between the rest of the bands
        if self.n_bands > 2:
            for i in range(1, self.n_bands):
                higher_band = data[:, i * band_length:(i + 1) * band_length]
                ratios.append(numpy.mean(higher_band) / numpy.mean(lower_band))
                lower_band = higher_band

        ratios = numpy.asarray(ratios, dtype=numpy.float64)
        return ratios


    def __call__(self, input_data, annotations):
        """Use VAD to filter out useless energy bands"""

        if self.features_processor is not None:
            feature_bands = self.features_processor(input_data, annotations)
            if feature_bands.any():
                ratios = self.compute_ratios(feature_bands)
                logger.info("- Extractions: computed ratios of size: %s ", str(ratios.shape))
                return ratios


from .spectrogram_extended import SpectrogramExtended
extractor = Ratios(features_processor=SpectrogramExtended())
