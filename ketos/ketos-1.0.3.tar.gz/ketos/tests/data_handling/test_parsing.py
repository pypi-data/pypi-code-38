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

""" Unit tests for the 'parsing' module within the ketos library
"""

import pytest
import json
import ketos.data_handling.parsing as jp

@pytest.fixture
def spectr_config_json_complete():
    j = '{"spectrogram": {"rate": "20 kHz", "window_size": "0.1 s", "step_size": "0.025 s", "window_function": "HAMMING", "low_frequency_cut": "30Hz", "high_frequency_cut": "3000Hz"}}'
    return j

@pytest.fixture
def spectr_config_json_partial():
    j = '{"spectrogram": {"rate": "20 kHz", "window_size": "0.1 s"}}'
    return j

@pytest.fixture
def one_frequency_band_json():
    j = '{"frequency_bands": [{"name": "15.6Hz", "range": ["11.0Hz", "22.1Hz"]}]}'
    return j

@pytest.fixture
def two_frequency_bands_json():
    j = '{"frequency_bands": [{"name": "15.6Hz", "range": ["11.0Hz", "22.1Hz"]},{"name": "test", "range": ["9kHz", "10kHz"]}]}'
    return j

@pytest.fixture
def frequency_band_without_name_json():
    j = '{"frequency_bands": [{"range": ["11.0Hz", "22.1Hz"]}]}'
    return j

@pytest.mark.test_parse_spectrogram_configuration
def test_parse_complete_spectrogram_config(spectr_config_json_complete):
    data = json.loads(spectr_config_json_complete)
    cfg = jp.parse_spectrogram_configuration(data['spectrogram'])
    assert cfg.rate == 20000
    assert cfg.window_size == 0.1
    assert cfg.step_size == 0.025
    assert cfg.window_function == jp.WinFun.HAMMING
    assert cfg.low_frequency_cut == 30
    assert cfg.high_frequency_cut == 3000

@pytest.mark.test_parse_spectrogram_configuration
def test_parse_partial_spectrogram_config(spectr_config_json_partial):
    data = json.loads(spectr_config_json_partial)
    cfg = jp.parse_spectrogram_configuration(data['spectrogram'])
    assert cfg.rate == 20000
    assert cfg.window_size == 0.1
    assert cfg.step_size == None
    assert cfg.window_function == None    

@pytest.mark.test_parse_frequency_bands
def test_parse_one_frequency_band(one_frequency_band_json):
    data = json.loads(one_frequency_band_json)
    band_name, freq_interval = jp.parse_frequency_bands(data['frequency_bands'])
    assert len(band_name) == 1
    assert band_name[0] == '15.6Hz'
    assert freq_interval[0].low == 11.0
    assert freq_interval[0].high == 22.1

@pytest.mark.test_parse_frequency_bands
def test_parse_two_frequency_bands(two_frequency_bands_json):
    data = json.loads(two_frequency_bands_json)
    band_name, freq_interval = jp.parse_frequency_bands(data['frequency_bands'])
    assert len(band_name) == 2
    assert band_name[1] == 'test'
    assert freq_interval[1].low == 9000.0
    assert freq_interval[1].high == 10000.0

@pytest.mark.test_parse_frequency_bands
def test_parse_frequency_band_without_name(frequency_band_without_name_json):
    data = json.loads(frequency_band_without_name_json)
    with pytest.raises(AssertionError):
        _, _ = jp.parse_frequency_bands(data['frequency_bands'])