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

""" Unit tests for the 'spectrogram_filters' module within the ketos library
"""

import pytest
import numpy as np
from ketos.audio_processing.spectrogram import MagSpectrogram
import ketos.audio_processing.spectrogram_filters as filters
from ketos.data_handling.parsing import Interval
import matplotlib.pyplot  as plt

def test_FAV_threshold_filter():
    spec = MagSpectrogram()
    spec.image = np.ones(shape=(100,100))
    spec.image[:,::10] = 10
    f = filters.FAVThresholdFilter(threshold=3.0, winlen=1)
    f.apply(spec)
    assert np.all(spec.image[:,0] == 9)
    assert np.all(spec.image[:,1] == 0.1)

def test_FAV_threshold_filter_w_winlen():
    spec = MagSpectrogram()
    spec.image = np.ones(shape=(100,100))
    spec.image[:,::10] = 10
    f = filters.FAVThresholdFilter(threshold=0.1, winlen=9)
    f.apply(spec)
    assert np.all(spec.image[:,0] == 9)
    assert np.all(spec.image[:,1] == 0.1)

def test_FAV_filter():
    spec = MagSpectrogram()
    spec.image = np.ones(shape=(100,100))
    spec.image[:,::10] = 10
    f = filters.FAVFilter(winlen=1)
    f.apply(spec)
    assert np.all(spec.image[:,9] == 531441)
    assert np.all(spec.image[:,19] == 531441)

def test_FAV_filter_w_smoothing():
    spec = MagSpectrogram()
    spec.image = np.ones(shape=(100,100))
    spec.image[:,::20] = 100
    f = filters.FAVFilter(winlen=5)
    f.apply(spec)
    assert np.all(spec.image[:,19] == pytest.approx(4.7318e8, abs=0.001e8))
    assert np.all(spec.image[:,39] == pytest.approx(4.7318e8, abs=0.001e8))

def test_harmonic_filter():
    spec = MagSpectrogram()
    spec.image = np.zeros(shape=(100,100))
    spec.image[:,::10] = 1
    f = filters.HarmonicFilter()
    f.apply(spec)
    x = np.argmax(spec.image, axis=1)
    assert np.all(x == 9)

def test_cropping_filter():
    spec = MagSpectrogram()
    spec.image = np.zeros(shape=(100,100))
    spec.fres = 0.2
    spec.image[:,51] = 1
    f = filters.CroppingFilter(flow=10.0, fhigh=18.1)
    f.apply(spec)
    assert spec.image.shape[1] == 41
    assert np.any(spec.image[:,1] == 1)

def test_frequency_filter():
    spec = MagSpectrogram()
    spec.image = np.zeros(shape=(100,100))
    spec.fres = 20.0
    spec.image[:,6] = np.arange(spec.image.shape[0])
    avg = np.average(spec.image[:,5:15], axis=1)
    names = ['band_A', 'band_B']
    bands = [Interval(100,300), Interval(1000,1400)]
    f = filters.FrequencyFilter(bands=bands, names=names)
    f.apply(spec)
    assert spec.image.shape[1] == len(bands)
    assert spec.flabels[0] == 'band_A'
    assert spec.flabels[1] == 'band_B'
    assert np.all(spec.image[:,0] == avg)

def test_window_filter():
    spec = MagSpectrogram()
    spec.image = np.zeros(shape=(100,100))
    spec.image[:,6] = np.arange(spec.image.shape[0])
    f = filters.WindowFilter(window_size=10, step_size=3)
    f.apply(spec)
    assert spec.image.shape[0] == 34
    assert spec.image[0,6] == 5
    assert spec.image[1,6] == 8

def test_window_subtraction_filter():
    spec = MagSpectrogram()
    spec.image = np.zeros(shape=(100,100))
    spec.image[:,6] = np.arange(spec.image.shape[0])
    f = filters.WindowSubtractionFilter(window_size=10)
    f.apply(spec)
    assert spec.image[0,6] == -5
    assert spec.image[1,6] == -4
