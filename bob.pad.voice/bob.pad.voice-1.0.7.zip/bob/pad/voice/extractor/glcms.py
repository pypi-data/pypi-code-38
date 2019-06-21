#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Tue 17 May 15:43:22 CEST 2016

import numpy
import bob.io.base
import bob.ip.base
import bob.sp

import math

from .ratios import Ratios

import logging

logger = logging.getLogger("bob.pad.voice")


class GLCMs(Ratios):
    """
    Extractor that computes histograms of LBP features from a textogram, which, in turn, is computed by a cepstral
    or spectral extractor passed as an argument.
    """

    def __init__(self,
                 features_processor,  # another extractor that provides features for LBP computation
                 n_glcms=1,  # do not split the features on which we compute GLCM
                 offset_vector=[[0, 1], [1, 0]],
                 properties=True,
                 **kwargs
                 ):
        Ratios.__init__(self,
                        features_processor=features_processor,
                        n_bands=n_glcms,
                           **kwargs)
        self.offset_vector = offset_vector
        self.properties = properties
        self.properties_list = ["angular_second_moment", "energy", "variance", "contrast",
                                "auto_correlation", "correlation", "correlation_matlab",
                                "inverse_difference_moment", "sum_average", "sum_variance",
                                "sum_entropy", "entropy", "difference_variance", "difference_entropy",
                                "dissimilarity", "homogeneity", "cluster_prominence", "cluster_shade",
                                "maximum_probability", "information_measure_of_correlation_1",
                                "information_measure_of_correlation_2", "inverse_difference",
                                "inverse_difference_normalized", "inverse_difference_moment_normalized"]
        self.offset = numpy.array(self.offset_vector, dtype='int32')


    def compute_glcms(self, data):
        # find the size of each textogram (a stip of features, for which we compute LBP)
        textogram_width = math.floor(self.features_processor.n_filters / self.n_bands)

        glcm_feats = []
        glcm_op = bob.ip.base.GLCM(levels=8)
        glcm_op.offset = self.offset

        for i in range(0, self.n_bands):
            textogram = data[:, i * textogram_width:(i + 1) * textogram_width]
            if textogram.max():
                textogram *= 255.0 / textogram.max()
            textogram = numpy.asarray(textogram, dtype=numpy.uint8)

            glcm_feat = numpy.ndarray((1, len(self.properties_list) * len(self.offset)), 'float64')
            glcm_feat.fill(numpy.NAN)
            glcm = glcm_op.extract(textogram)

            if self.properties:
                try:
                    glcm_prop = glcm_op.properties_by_name(glcm, self.properties_list)
                    glcm_feat = [x.tolist() for x in glcm_prop]  # we get list of lists of features
                    glcm_feat = numpy.asarray(glcm_feat, dtype=numpy.float64)
                    glcm_feat.flatten()
                    glcm_feat[glcm_feat < -1024] = -1024  # temporary hack excluding extreemly small values
                except ValueError as e:
                    logger.error("- Extraction: Exceptions with GLCM properties computation: %s", repr(e))
                naninfeat = numpy.isnan(glcm_feat)
                if naninfeat.any():
                    glcm_feat[naninfeat] = 0
                    logger.warn("- Extraction: GLCM features have NaNs!")
            else:
                glcm_feat = glcm.flatten()

            glcm_feats = numpy.append(glcm_feats, glcm_feat)

        return glcm_op, glcm_feats

    def get_features(self, input_data, annotations):
        # spectrogram = SpectrogramExtended.__call__(input_data, annotations)
        if self.features_processor is not None:
            return self.features_processor(input_data, annotations)

        logger.info("- Extraction: spectrogram is empty, returning zero vector...")
        return numpy.array([numpy.zeros(len(self.properties_list)*len(self.offset))])

    def __call__(self, input_data, annotations=None):
        """Computed LBP histograms from cepstral or spectrogram features"""

        # spectrogram = SpectrogramExtended.__call__(input_data, annotations)
        spectrogram = self.get_features(input_data, annotations)

        glcm, glcm_features = self.compute_glcms(spectrogram)
        ratios = []
        if self.band_ratios:
            ratios = self.compute_ratios(spectrogram)

        # concatenate histograms together in one numpy array
        features = []
        for i in range(0, self.n_bands):
            features.append(glcm_features[i].flatten())  # just put into the larger list

        features = numpy.append(ratios, features)
        logger.info("- Extraction: size of the GLCM-based feature vector of size %s", str(features.shape))

        return numpy.asarray(features, dtype=numpy.float64)


from .spectrogram_extended import SpectrogramExtended
extractor = GLCMs(features_processor=SpectrogramExtended())

