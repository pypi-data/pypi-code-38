#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Mon  6 Aug 15:12:22 CEST 2015
#


from __future__ import print_function

import bob.measure
from bob.bio.base.extractor import Extractor
from .. import utils

import numpy
import bob.ap
import math

import logging
logger = logging.getLogger("bob.pad.voice")


class SpectrogramExtended(Extractor):
    """Extract energy bands from spectrogram and VAD labels based on the modulation of the energy around 4 Hz"""

    def __init__(
            self,
            win_length_ms=20.,  # 20 ms
            win_shift_ms=10.,  # 10 ms
            n_filters=40,
            f_min=0.0,  # 0 Hz
            f_max=4000,  # 4 KHz
            pre_emphasis_coef=1.0,
            mel_scale=True,
            rect_filter=False,
            inverse_filter=False,
            normalize_spectrum=False,
            log_filter=True,
            energy_filter=False,
            energy_bands=True,
            vad_filter="trim_silence",
            normalize_feature_vector = False,
            **kwargs
    ):
        # call base class constructor with its set of parameters
        Extractor.__init__(
            self,
            requires_training=False, split_training_data_by_client=False,
            **kwargs
        )
        # copy parameters
        self.win_length_ms = win_length_ms
        self.win_shift_ms = win_shift_ms
        self.n_filters = n_filters
        self.f_min = f_min
        self.f_max = f_max
        self.pre_emphasis_coef = pre_emphasis_coef
        self.mel_scale = mel_scale
        self.rect_filter = rect_filter
        self.inverse_filter = inverse_filter
        self.normalize_spectrum = normalize_spectrum
        self.log_filter = log_filter
        self.energy_filter = energy_filter
        self.energy_bands = energy_bands
        self.vad_filter = vad_filter
        self.normalize_feature_vector = normalize_feature_vector

        if self.energy_bands:
            self.features_len = self.n_filters
        else:
            self.features_len = int(math.pow(2.0, math.ceil(math.log(self.win_length_ms)/math.log(2))))


    def normalize_features(self, features):
        mean = numpy.mean(features, axis=0)
        std = numpy.std(features, axis=0)
        return numpy.divide(features - mean, std)


    def compute_spectrogram(self, rate, data):
        spectrogram = bob.ap.Spectrogram(rate, self.win_length_ms, self.win_shift_ms, self.n_filters,
                                         self.f_min, self.f_max, self.pre_emphasis_coef)

        spectrogram.energy_bands = self.energy_bands
        spectrogram.mel_scale = self.mel_scale
        spectrogram.rect_filter = self.rect_filter
        spectrogram.inverse_filter = self.inverse_filter
        spectrogram.normalize_spectrum = self.normalize_spectrum
        spectrogram.log_filter = self.log_filter
        spectrogram.energy_filter = self.energy_filter

        energy_bands = spectrogram(data)
        return energy_bands

    def __call__(self, input_data, annotations=None):
        """labels speech (1) and non-speech (0) parts of the given input wave file using 4Hz modulation
        energy and energy, as well as, compute energy of the signal and split it in bands using on linear or mel-filters
            Input parameter:
               * input_signal[0] --> rate
               * input_signal[1] --> signal
        """
        rate = input_data[0]
        wav_sample = input_data[1]
        labels = input_data[2]  # results of the VAD preprocessor

        # remove trailing zeros from the wav_sample
        # wav_sample = numpy.trim_zeros(wav_sample) # comment it out to align with VAD output

        if wav_sample.size:
            spectrogram = self.compute_spectrogram(rate, wav_sample)
            logger.info("- Extraction: size of spectrogram features %s", str(spectrogram.shape))

            filtered_spectrogram = utils.vad_filter_features(labels, spectrogram, self.vad_filter)
            logger.info("- Extraction: size of filtered spectrogram features %s", str(filtered_spectrogram.shape))

            if numpy.isnan(numpy.sum(filtered_spectrogram)):
                logger.error("- Extraction: cepstral coefficients have NaN values, returning zero-vector...")
                return numpy.array([numpy.zeros(self.features_len)])

            if self.normalize_feature_vector:
                filtered_spectrogram = self.normalize_features(filtered_spectrogram)

            return numpy.asarray(filtered_spectrogram, dtype=numpy.float64)

        logger.error("- Extraction: WAV sample is empty")
        return numpy.array([numpy.zeros(self.features_len)])


extractor = SpectrogramExtended()
